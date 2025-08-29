TARGET_SRC_DIR=.
TARGET_INC_DIR=.
TARGET_OUT_DIR=.
ISP_INC_DIR=$(TARGET_SRC_DIR)/include

OPENCV_LIB_DIR="/usr/lib/x86_64-linux-gnu"
# OpenCV flags (opencv4)
OPENCV_CFLAGS := $(shell pkg-config opencv4 --cflags 2>/dev/null)
OPENCV_LIBS   := $(shell pkg-config opencv4 --libs 2>/dev/null)

LDFLAGS += -L. -Wl,-rpath,'$$ORIGIN'
LDLIBS  += $(OPENCV_LIBS) -lusb-1.0 -lpthread -lm -lthermometry -lSimple -lpot

CPPFLAGS=-I $(TARGET_INC_DIR)  -I $(ISP_INC_DIR)  -Wl,-rpath=./libs/linux/x86-linux_libs $(OPENCV_CFLAGS)

sample:$(TARGET_SRC_DIR)/*.cpp
	g++ $(CPPFLAGS) -o $(TARGET_OUT_DIR)/$@ $^  -L ./libs/linux/x86-linux_libs  -L $(OPENCV_LIB_DIR) \
	-lpthread -liruvc -lirtemp -lirprocess -lirparse -lm \
	$(OPENCV_LIBS)
.PHONY:clean
clean:
	@rm -f sample
