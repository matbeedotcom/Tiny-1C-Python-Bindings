#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "include/all_config.h"
#include "include/libiruvc.h"
#include "include/libirtemp.h"
#include "include/libirparse.h"
#include "include/libirprocess.h"
#include "data.h"

namespace py = pybind11;

// Global variables to maintain state
static StreamFrameInfo_t g_stream_frame_info = {0};
static bool g_initialized = false;

class ThermalCamera {
private:
    bool is_open;
    bool is_streaming;

public:
    ThermalCamera() : is_open(false), is_streaming(false) {}
    
    ~ThermalCamera() {
        if (is_streaming) {
            stop_stream();
        }
        if (is_open) {
            close();
        }
    }

    bool open() {
        if (is_open) {
            return true;
        }
        
        int result = ir_camera_open(&g_stream_frame_info.camera_param);
        if (result == 0) {
            is_open = true;
            g_initialized = true;
            load_stream_frame_info(&g_stream_frame_info);
            command_init();
            return true;
        }
        return false;
    }

    bool close() {
        if (!is_open) {
            return true;
        }
        
        if (is_streaming) {
            stop_stream();
        }
        
        int result = ir_camera_close();
        is_open = false;
        g_initialized = false;
        return (result == 0);
    }

    bool start_stream() {
        if (!is_open || is_streaming) {
            return false;
        }
        
        int result = ir_camera_stream_on(&g_stream_frame_info);
        if (result == 0) {
            is_streaming = true;
            
            // For P2 series, wait 5 seconds then send y16_preview_start for temperature data
            #if defined(TEMP_OUTPUT) || defined(IMAGE_AND_TEMP_OUTPUT)
            sleep(5);  // Wait 5 seconds as per documentation
            result = y16_preview_start(PREVIEW_PATH0, Y16_MODE_TEMPERATURE);
            if (result < 0) {
                printf("y16_preview_start failed: %d\n", result);
            }
            #endif
            
            return true;
        }
        return false;
    }

    bool stop_stream() {
        if (!is_streaming) {
            return true;
        }
        
        int result = ir_camera_stream_off(&g_stream_frame_info);
        is_streaming = false;
        return (result == 0);
    }

    py::tuple get_camera_info() {
        if (!g_initialized) {
            return py::make_tuple(0, 0, 0);
        }
        
        return py::make_tuple(
            g_stream_frame_info.camera_param.width,
            g_stream_frame_info.camera_param.height,
            g_stream_frame_info.camera_param.fps
        );
    }

    py::array_t<uint16_t> get_temperature_frame() {
        if (!is_streaming || !g_initialized || g_stream_frame_info.temp_byte_size == 0) {
            return py::array_t<uint16_t>();
        }

        // Get a frame
        if (uvc_frame_get(g_stream_frame_info.raw_frame) < 0) {
            return py::array_t<uint16_t>();
        }

        // Cut raw data to separate image and temperature
        raw_data_cut((uint8_t*)g_stream_frame_info.raw_frame, 
                     g_stream_frame_info.image_byte_size,
                     g_stream_frame_info.temp_byte_size, 
                     (uint8_t*)g_stream_frame_info.image_frame,
                     (uint8_t*)g_stream_frame_info.temp_frame);

        // Create numpy array from temperature data
        size_t width = g_stream_frame_info.temp_info.width;
        size_t height = g_stream_frame_info.temp_info.height;
        
        auto result = py::array_t<uint16_t>(
            {height, width},
            {sizeof(uint16_t) * width, sizeof(uint16_t)},
            (uint16_t*)g_stream_frame_info.temp_frame
        );
        
        return result;
    }

    py::array_t<uint8_t> get_image_frame() {
        if (!is_streaming || !g_initialized) {
            return py::array_t<uint8_t>();
        }

        // Get a frame
        if (uvc_frame_get(g_stream_frame_info.raw_frame) < 0) {
            return py::array_t<uint8_t>();
        }

        // Cut raw data to separate image and temperature
        raw_data_cut((uint8_t*)g_stream_frame_info.raw_frame, 
                     g_stream_frame_info.image_byte_size,
                     g_stream_frame_info.temp_byte_size, 
                     (uint8_t*)g_stream_frame_info.image_frame,
                     (uint8_t*)g_stream_frame_info.temp_frame);

        // Process image frame
        size_t width = g_stream_frame_info.image_info.width;
        size_t height = g_stream_frame_info.image_info.height;
        
        // Assuming BGR888 output format (3 channels)
        auto result = py::array_t<uint8_t>(
            {height, width, 3},
            {sizeof(uint8_t) * width * 3, sizeof(uint8_t) * 3, sizeof(uint8_t)},
            (uint8_t*)g_stream_frame_info.image_frame
        );
        
        return result;
    }

    bool is_camera_open() const { return is_open; }
    bool is_camera_streaming() const { return is_streaming; }
};

class TemperatureProcessor {
public:
    static float temp_value_to_celsius(uint16_t temp_val) {
        return temp_value_converter(temp_val);
    }

    static py::tuple get_point_temperature(py::array_t<uint16_t> temp_data, int x, int y) {
        if (temp_data.ndim() != 2) {
            return py::make_tuple(false, 0.0f);
        }
        
        auto buf = temp_data.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        
        TempDataRes_t temp_res = {(uint16_t)buf.shape[1], (uint16_t)buf.shape[0]};
        Dot_t point = {(uint16_t)x, (uint16_t)y};
        uint16_t temp = 0;
        
        if (get_point_temp(ptr, temp_res, point, &temp) == IRTEMP_SUCCESS) {
            return py::make_tuple(true, temp_value_converter(temp));
        }
        
        return py::make_tuple(false, 0.0f);
    }

    static py::tuple get_rect_temperature(py::array_t<uint16_t> temp_data, int x, int y, int width, int height) {
        if (temp_data.ndim() != 2) {
            return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
        }
        
        auto buf = temp_data.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        
        TempDataRes_t temp_res = {(uint16_t)buf.shape[1], (uint16_t)buf.shape[0]};
        Area_t rect = {(uint16_t)x, (uint16_t)y, (uint16_t)width, (uint16_t)height};
        TempInfo_t temp_info = {0};
        
        if (get_rect_temp(ptr, temp_res, rect, &temp_info) == IRTEMP_SUCCESS) {
            return py::make_tuple(
                true,
                temp_value_converter(temp_info.max_temp),
                temp_value_converter(temp_info.min_temp),
                temp_value_converter(temp_info.avr_temp)
            );
        }
        
        return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
    }

    static py::tuple get_line_temperature(py::array_t<uint16_t> temp_data, int x1, int y1, int x2, int y2) {
        if (temp_data.ndim() != 2) {
            return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
        }
        
        auto buf = temp_data.request();
        uint16_t* ptr = (uint16_t*)buf.ptr;
        
        TempDataRes_t temp_res = {(uint16_t)buf.shape[1], (uint16_t)buf.shape[0]};
        Line_t line = {(uint16_t)x1, (uint16_t)y1, (uint16_t)x2, (uint16_t)y2};
        TempInfo_t temp_info = {0};
        
        if (get_line_temp(ptr, temp_res, line, &temp_info) == IRTEMP_SUCCESS) {
            return py::make_tuple(
                true,
                temp_value_converter(temp_info.max_temp),
                temp_value_converter(temp_info.min_temp),
                temp_value_converter(temp_info.avr_temp)
            );
        }
        
        return py::make_tuple(false, 0.0f, 0.0f, 0.0f);
    }
};

PYBIND11_MODULE(thermal_camera, m) {
    m.doc() = "Python bindings for Thermal Camera SDK";
    
    py::class_<ThermalCamera>(m, "ThermalCamera")
        .def(py::init<>())
        .def("open", &ThermalCamera::open, "Open the thermal camera")
        .def("close", &ThermalCamera::close, "Close the thermal camera")
        .def("start_stream", &ThermalCamera::start_stream, "Start camera streaming")
        .def("stop_stream", &ThermalCamera::stop_stream, "Stop camera streaming")
        .def("get_camera_info", &ThermalCamera::get_camera_info, "Get camera information (width, height, fps)")
        .def("get_temperature_frame", &ThermalCamera::get_temperature_frame, "Get temperature frame as numpy array")
        .def("get_image_frame", &ThermalCamera::get_image_frame, "Get image frame as numpy array")
        .def("is_open", &ThermalCamera::is_camera_open, "Check if camera is open")
        .def("is_streaming", &ThermalCamera::is_camera_streaming, "Check if camera is streaming");
    
    py::class_<TemperatureProcessor>(m, "TemperatureProcessor")
        .def_static("temp_to_celsius", &TemperatureProcessor::temp_value_to_celsius, 
                   "Convert temperature value to Celsius")
        .def_static("get_point_temp", &TemperatureProcessor::get_point_temperature,
                   "Get temperature at specific point (x, y)")
        .def_static("get_rect_temp", &TemperatureProcessor::get_rect_temperature,
                   "Get temperature statistics for rectangle area")
        .def_static("get_line_temp", &TemperatureProcessor::get_line_temperature,
                   "Get temperature statistics along a line");
    
    // Utility functions
    m.def("temp_to_celsius", &temp_value_converter, "Convert raw temperature value to Celsius");
}