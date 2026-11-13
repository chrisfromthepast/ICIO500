TARGET = icio500_daisyverb
APP_TYPE = BOOT_SRAM

# Select algorithm target: dattorro.cpp, zita.cpp, FDN_stereo.cpp, or freeverb_stereo.cpp
ALGO_SRC ?= dattorro.cpp
CPP_SOURCES = $(ALGO_SRC)

LIBDAISY_DIR ?= ../../libDaisy
CFLAGS += -O3 -I../common

SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
include $(SYSTEM_FILES_DIR)/Makefile
