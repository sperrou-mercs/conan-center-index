import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, collect_libs

class PortAudio(ConanFile):
    name = "portaudio"
    description = "Free, cross-platform, open-source, audio I/O library"
    url = "www.portaudio.com"
    license = "PortAudio"
    revision_mode = "scm"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    def build_requirements(self):
        """Define runtime requirements."""
        if self.settings.os == "Linux":
            # Build requirements because we need it to build but we do not want to use it on dev 
            # machines or include it in packages.
            self.build_requires("libalsa/1.2.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def config_options(self):
        """fPIC is linux only."""
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            self.options.shared = True
            self.options["libalsa"].shared = True

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PA_ENABLE_DEBUG_OUTPUT"]=  self.settings.build_type != "Release",
        tc.variables["PA_BUILD_EXAMPLES"]=  False,
        tc.variables["PA_BUILD_TESTS"]=  False,
        tc.variables["PA_DLL_LINK_WITH_STATIC_RUNTIME"]=  False
        if self.settings.os == "Linux":
            alsa_info = self.deps_cpp_info["libalsa"]
            tc.variables["ALSA_INCLUDE_DIR"] = alsa_info.include_paths[0]
            tc.variables["ALSA_LIBRARY"] = os.path.join(alsa_info.lib_paths[0], "libasound.{}".format("so" if self.options.shared else "a"))
            tc.variables["PA_USE_ALSA"] = True
            tc.variables["PA_USE_JACK"] = False
        elif self.settings.os == "Windows":
            tc.variables["PA_USE_MME"] = True
            tc.variables["PA_USE_WDMKS_DEVICE_INFO"] = False
            tc.variables["PA_UNICODE_BUILD"] = False
            tc.variables["PA_USE_WASAPI"] = False
            tc.variables["PA_USE_WDMKS"] = False
            tc.variables["PA_USE_ASIO"] = False
            tc.variables["PA_USE_DS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "portaudio")
        self.cpp_info.set_property("cmake_target_name", "portaudio")
        self.cpp_info.libs = collect_libs(self)
        if self.options.shared:
            if self.settings.os == "Windows":
                self.env_info.PATH.append(os.path.join( self.package_folder, "bin"))
            else:
                self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))