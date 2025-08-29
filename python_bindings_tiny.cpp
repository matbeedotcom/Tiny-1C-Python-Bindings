#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

// When using pre-built libraries on Windows, we need to import symbols
#ifdef _WIN32
    #define DLLEXPORT __declspec(dllimport)
#endif

// Include only the header files - we'll link to the libraries
#include "include/all_config.h"
#include "include/libiruvc.h"
#include "include/libirtemp.h"
#include "include/libirparse.h"
#include "include/libirprocess.h"
#include "include/thermal_cam_cmd.h"

// Platform-specific includes for sleep
#ifdef _WIN32
    #include <windows.h>
    #define platform_sleep(seconds) Sleep((seconds) * 1000)
#else
    #include <unistd.h>
    #define platform_sleep(seconds) sleep(seconds)
#endif

namespace py = pybind11;

// Simple wrapper that uses only the basic library functions
class TinyThermalCamera {
private:
    bool is_initialized;
    bool is_open;
    bool is_streaming;
    CameraParam_t camera_param;
    uint8_t* raw_frame_buffer;
    uint8_t* image_frame_buffer;
    uint8_t* temp_frame_buffer;
    uint32_t frame_size;
    uint32_t image_width, image_height;
    uint32_t temp_width, temp_height;

public:
    TinyThermalCamera() : is_initialized(false), is_open(false), is_streaming(false),
                           raw_frame_buffer(nullptr), image_frame_buffer(nullptr), 
                           temp_frame_buffer(nullptr), frame_size(0) {}
    
    ~TinyThermalCamera() {
        cleanup();
    }

    bool initialize() {
        if (is_initialized) return true;
        
        int result = uvc_camera_init();
        if (result == IRUVC_SUCCESS) {
            is_initialized = true;
            return true;
        }
        return false;
    }

    py::tuple get_device_list() {
        if (!is_initialized && !initialize()) {
            return py::make_tuple(false, py::list());
        }

        DevCfg_t devs_cfg[64] = {0};
        int result = uvc_camera_list(devs_cfg);
        
        if (result < 0) {
            return py::make_tuple(false, py::list());
        }

        py::list devices;
        for (int i = 0; i < 64 && devs_cfg[i].vid != 0; i++) {
            py::dict device;
            device["vid"] = devs_cfg[i].vid;
            device["pid"] = devs_cfg[i].pid;
            device["name"] = devs_cfg[i].name ? std::string(devs_cfg[i].name) : "";
            devices.append(device);
        }

        return py::make_tuple(true, devices);
    }

    bool open_camera(int vid = 0x0BDA, int pid = 0x5840) {
        if (is_open) return true;
        if (!is_initialized && !initialize()) return false;

        DevCfg_t devs_cfg[64] = {0};
        int result = uvc_camera_list(devs_cfg);
        if (result < 0) return false;

        // Find the device
        int dev_index = -1;
        for (int i = 0; i < 64; i++) {
            if (devs_cfg[i].vid == vid && devs_cfg[i].pid == pid) {
                dev_index = i;
                break;
            }
        }

        if (dev_index < 0) return false;

        // Get camera stream info
        CameraStreamInfo_t stream_info[32] = {0};
        result = uvc_camera_info_get(devs_cfg[dev_index], stream_info);
        if (result < 0) return false;

        // Open the camera
        result = uvc_camera_open(devs_cfg[dev_index]);
        if (result < 0) return false;

        // Initialize command system for P2 series cameras
        vdcmd_set_polling_wait_time(10000);
        vdcmd_init();

        // Set up camera parameters (use first available stream)
        camera_param.dev_cfg = devs_cfg[dev_index];
        camera_param.format = stream_info[0].format;
        camera_param.width = stream_info[0].width;
        camera_param.height = stream_info[0].height;
        camera_param.fps = stream_info[0].fps[0];
        camera_param.timeout_ms_delay = 1000;
        camera_param.frame_size = camera_param.width * camera_param.height * 2;

        // For IMAGE_AND_TEMP_OUTPUT mode, image and temp are half the height each
        image_width = camera_param.width;
        image_height = camera_param.height / 2;
        temp_width = camera_param.width;
        temp_height = camera_param.height / 2;

        frame_size = camera_param.frame_size;
        is_open = true;
        return true;
    }

    bool start_streaming(bool enable_temperature_mode = true, int wait_seconds = 5) {
        if (!is_open || is_streaming) return false;

        // Allocate frame buffers
        raw_frame_buffer = new uint8_t[frame_size];
        image_frame_buffer = new uint8_t[image_width * image_height * 3]; // BGR888
        temp_frame_buffer = new uint8_t[temp_width * temp_height * 2];   // 16-bit

        int result = uvc_camera_stream_start(camera_param, nullptr);
        if (result < 0) {
            delete[] raw_frame_buffer;
            delete[] image_frame_buffer;
            delete[] temp_frame_buffer;
            raw_frame_buffer = nullptr;
            image_frame_buffer = nullptr;
            temp_frame_buffer = nullptr;
            return false;
        }

        is_streaming = true;

        // For P2 series cameras, need to wait then send y16_preview_start command
        if (enable_temperature_mode) {
            printf("Waiting %d seconds for camera stabilization before enabling temperature mode...\n", wait_seconds);
            platform_sleep(wait_seconds);
            
            // Send y16_preview_start command to switch to temperature data output
            printf("Sending y16_preview_start command to enable temperature mode...\n");
            result = y16_preview_start(PREVIEW_PATH0, Y16_MODE_TEMPERATURE);
            if (result < 0) {
                printf("Warning: y16_preview_start failed with error %d\n", result);
                printf("Camera may not be outputting temperature data.\n");
            } else {
                printf("Temperature mode enabled successfully.\n");
            }
        }

        return true;
    }

    bool stop_streaming() {
        if (!is_streaming) return true;

        int result = uvc_camera_stream_close(KEEP_CAM_SIDE_PREVIEW);
        is_streaming = false;
        return (result >= 0);
    }

    bool close_camera() {
        if (!is_open) return true;

        if (is_streaming) {
            stop_streaming();
        }

        uvc_camera_close();
        is_open = false;
        return true;
    }

    py::tuple get_camera_info() {
        if (!is_open) {
            return py::make_tuple(0, 0, 0);
        }
        return py::make_tuple(camera_param.width, camera_param.height, camera_param.fps);
    }

    py::array_t<uint16_t> get_raw_frame() {
        if (!is_streaming || !raw_frame_buffer) {
            return py::array_t<uint16_t>();
        }

        int result = uvc_frame_get(raw_frame_buffer);
        if (result < 0) {
            return py::array_t<uint16_t>();
        }

        // Return raw frame as uint16 array
        size_t height = camera_param.height;
        size_t width = camera_param.width;
        
        auto raw_array = py::array_t<uint16_t>(
            {height, width},
            {sizeof(uint16_t) * width, sizeof(uint16_t)},
            (uint16_t*)raw_frame_buffer
        );
        
        return raw_array;
    }

    bool is_camera_open() const { return is_open; }
    bool is_camera_streaming() const { return is_streaming; }

private:
    void cleanup() {
        if (is_streaming) {
            stop_streaming();
        }
        if (is_open) {
            close_camera();
        }
        if (is_initialized) {
            uvc_camera_release();
            is_initialized = false;
        }
        if (raw_frame_buffer) {
            delete[] raw_frame_buffer;
            raw_frame_buffer = nullptr;
        }
        if (image_frame_buffer) {
            delete[] image_frame_buffer;
            image_frame_buffer = nullptr;
        }
        if (temp_frame_buffer) {
            delete[] temp_frame_buffer;
            temp_frame_buffer = nullptr;
        }
    }

public:
    // Context manager support
    TinyThermalCamera& __enter__() {
        if (!initialize()) {
            throw std::runtime_error("Failed to initialize camera system");
        }
        if (!open_camera()) {
            throw std::runtime_error("Failed to open camera");
        }
        return *this;
    }
    
    void __exit__(py::object exc_type, py::object exc_value, py::object traceback) {
        // Context manager only handles initialization and opening
        // Stream and camera connection should persist for continued use
        // User must explicitly call stop_stream() and close() when done
        // This allows the camera object to be used after the 'with' block
    }
    
    // Convenience methods for wrapper compatibility
    py::tuple capture_frame() {
        py::array_t<uint16_t> temp_frame = get_raw_frame();
        py::array_t<uint8_t> image_frame; // Empty for now, could be expanded
        return py::make_tuple(temp_frame, image_frame);
    }
    
    py::dict get_temperature_stats(py::array_t<uint16_t> temp_frame) {
        if (temp_frame.size() == 0) {
            return py::dict();
        }
        
        auto buf = temp_frame.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        size_t size = temp_frame.size();
        
        uint16_t min_raw = 65535, max_raw = 0;
        uint64_t sum_raw = 0;
        
        for (size_t i = 0; i < size; i++) {
            uint16_t val = ptr[i];
            if (val < min_raw) min_raw = val;
            if (val > max_raw) max_raw = val;
            sum_raw += val;
        }
        
        // Local temperature conversion
        auto to_celsius = [](uint16_t temp_val) { return ((double)temp_val / 64.0 - 273.15); };
        
        py::dict stats;
        stats["min"] = to_celsius(min_raw);
        stats["max"] = to_celsius(max_raw);
        stats["mean"] = to_celsius(sum_raw / size);
        stats["range"] = to_celsius(max_raw) - to_celsius(min_raw);
        
        return stats;
    }
    
    py::tuple find_hotspot(py::array_t<uint16_t> temp_frame) {
        if (temp_frame.ndim() != 2 || temp_frame.size() == 0) {
            return py::make_tuple(py::make_tuple(0, 0), 0.0f);
        }
        
        auto buf = temp_frame.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        
        uint16_t max_temp = 0;
        int max_x = 0, max_y = 0;
        
        for (int y = 0; y < buf.shape[0]; y++) {
            for (int x = 0; x < buf.shape[1]; x++) {
                uint16_t temp = ptr[y * buf.shape[1] + x];
                if (temp > max_temp) {
                    max_temp = temp;
                    max_x = x;
                    max_y = y;
                }
            }
        }
        
        // Local temperature conversion
        auto to_celsius = [](uint16_t temp_val) { return ((double)temp_val / 64.0 - 273.15); };
        
        return py::make_tuple(py::make_tuple(max_x, max_y), to_celsius(max_temp));
    }
};

class TemperatureProcessor {
public:
    static float temp_to_celsius(uint16_t temp_val) {
        return ((double)temp_val / 64.0 - 273.15);
    }

    static py::tuple get_point_temperature(py::array_t<uint16_t> temp_data, int x, int y) {
        if (temp_data.ndim() != 2) {
            return py::make_tuple(false, 0.0f);
        }
        
        auto buf = temp_data.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        
        if (x < 0 || x >= buf.shape[1] || y < 0 || y >= buf.shape[0]) {
            return py::make_tuple(false, 0.0f);
        }
        
        uint16_t temp_raw = ptr[y * buf.shape[1] + x];
        float temp_celsius = temp_to_celsius(temp_raw);
        
        return py::make_tuple(true, temp_celsius);
    }

    static py::tuple get_rect_temperature(py::array_t<uint16_t> temp_data, int x, int y, int width, int height) {
        if (temp_data.ndim() != 2) {
            return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
        }
        
        auto buf = temp_data.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        
        int img_width = buf.shape[1];
        int img_height = buf.shape[0];
        
        // Bounds checking
        if (x < 0 || y < 0 || x + width > img_width || y + height > img_height) {
            return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
        }
        
        uint16_t min_temp = 65535, max_temp = 0;
        uint32_t sum_temp = 0;
        int count = 0;
        
        for (int row = y; row < y + height; row++) {
            for (int col = x; col < x + width; col++) {
                uint16_t temp = ptr[row * img_width + col];
                if (temp < min_temp) min_temp = temp;
                if (temp > max_temp) max_temp = temp;
                sum_temp += temp;
                count++;
            }
        }
        
        if (count == 0) {
            return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
        }
        
        float max_celsius = temp_to_celsius(max_temp);
        float min_celsius = temp_to_celsius(min_temp);
        float avg_celsius = temp_to_celsius(sum_temp / count);
        
        return py::make_tuple(true, max_celsius, min_celsius, avg_celsius);
    }
};

PYBIND11_MODULE(tiny_thermal_camera, m) {
    m.doc() = "Python bindings for Tiny Thermal Camera SDK";
    
    py::class_<TinyThermalCamera>(m, "ThermalCamera")
        .def(py::init<>())
        .def("initialize", &TinyThermalCamera::initialize, "Initialize the camera system")
        .def("get_device_list", &TinyThermalCamera::get_device_list, "Get list of available thermal cameras")
        .def("open", &TinyThermalCamera::open_camera, "Open thermal camera", 
             py::arg("vid") = 0x0BDA, py::arg("pid") = 0x5840)
        .def("close", &TinyThermalCamera::close_camera, "Close thermal camera")
        .def("start_stream", &TinyThermalCamera::start_streaming, "Start camera streaming",
             py::arg("enable_temperature_mode") = true,
             py::arg("wait_seconds") = 5)
        .def("start_streaming", &TinyThermalCamera::start_streaming, "Start camera streaming (alias)",
             py::arg("enable_temperature_mode") = true,
             py::arg("wait_seconds") = 5)
        .def("stop_stream", &TinyThermalCamera::stop_streaming, "Stop camera streaming")
        .def("get_camera_info", &TinyThermalCamera::get_camera_info, "Get camera information (width, height, fps)")
        .def("get_raw_frame", &TinyThermalCamera::get_raw_frame, "Get raw frame as numpy array")
        .def("is_open", &TinyThermalCamera::is_camera_open, "Check if camera is open")
        .def("is_streaming", &TinyThermalCamera::is_camera_streaming, "Check if camera is streaming")
        .def("__enter__", &TinyThermalCamera::__enter__, "Context manager entry")
        .def("__exit__", &TinyThermalCamera::__exit__, "Context manager exit")
        .def("capture_frame", &TinyThermalCamera::capture_frame, "Capture temperature and image frames")
        .def("get_temperature_stats", &TinyThermalCamera::get_temperature_stats, "Get temperature statistics")
        .def("find_hotspot", &TinyThermalCamera::find_hotspot, "Find hottest point in temperature frame");
    
    py::class_<TemperatureProcessor>(m, "TemperatureProcessor")
        .def_static("temp_to_celsius", &TemperatureProcessor::temp_to_celsius, 
                   "Convert raw temperature value to Celsius")
        .def_static("get_point_temp", &TemperatureProcessor::get_point_temperature,
                   "Get temperature at specific point (x, y)")
        .def_static("get_rect_temp", &TemperatureProcessor::get_rect_temperature,
                   "Get temperature statistics for rectangle area");
    
    // Utility functions
    m.def("temp_to_celsius", &TemperatureProcessor::temp_to_celsius, "Convert raw temperature value to Celsius");
}