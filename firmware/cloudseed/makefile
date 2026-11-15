TARGET = icio500_cloudseed

# Bootloader target so users can swap firmwares via Web Programmer / DFU
APP_TYPE = BOOT_SRAM

CPP_SOURCES = main.cpp \
              $( wildcard CloudSeed/*.cpp ) \
              $( wildcard CloudSeed/AudioLib/*.cpp )

LIBDAISY_DIR = ../../libDaisy
CFLAGS += -O3 -I. -ICloudSeed

SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
include $(SYSTEM_FILES_DIR)/Makefile
