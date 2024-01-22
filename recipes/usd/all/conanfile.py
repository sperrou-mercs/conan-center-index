import os
from conan import ConanFile
from conan.tools.files import chdir, copy, get, load, download, replace_in_file, rm, rmdir, collect_libs, export_conandata_patches, apply_conandata_patches
from conan.tools.cmake import cmake_layout, CMakeDeps, CMakeToolchain, CMake

class USDConan(ConanFile):
    name = "usd"
    url = "https://graphics.pixar.com/usd/docs/index.html"
    description = "Universal scene description"
    license = "Modified Apache 2.0 License"
    settings = "os", "compiler", "build_type", "arch"
    revision_mode = "scm"
    options = {"shared": [True, False], "fPIC": [True, False], "with_python": [True, False], "with_qt": [True, False], "debug_symbols": [True, False], "use_imaging": [True, False]}
    default_options = "shared=True", "fPIC=True", "with_python=True", "with_qt=False", "debug_symbols=False", "use_imaging=True", "*:shared=False", "glew:shared=True", "tbb:shared=True", "*:fPIC=True", "boost:i18n_backend=icu", "boost:zstd=True", "boost:lzma=True"
    short_paths = True

    def requirements(self):
        """Define runtime requirements."""
        self.requires("alembic/1.8.5")
        self.requires("boost/1.73")
        self.requires("hdf5/[>=1 <2]")
        self.requires("materialx/1.37.1")
        if self.options.use_imaging:
            self.requires("opencolorio/2.1.3")
            self.requires("openimageio/2.3.21.0")
            self.requires("ptex/2.4.0")
        self.requires("opensubdiv/3.5.1")
        self.requires("tbb/2020.2")
        self.requires("zlib/1.2.11")
        #self.requires("glu/9.0.1")
        #self.requires("glew/2.1.0")
        if self.options.with_python:
            self.requires("cpython/3.7.12")
        if self.options.with_qt:
            self.requires("qt/5.15.12")

    def config_options(self):
        """fPIC is linux only."""
        if self.settings.os != "Linux":
            self.options.remove("fPIC")
            
    def layout(self):
        cmake_layout(self)
            
    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PXR_BUILD_ALEMBIC_PLUGIN"] = True
        # tc.variables["PXR_BUILD_DOCUMENTATION"] = False
        # tc.variables["PXR_BUILD_DRACO_PLUGIN"] = False
        # tc.variables["PXR_BUILD_EMBREE_PLUGIN"] = False
        # tc.variables["PXR_BUILD_HOUDINI_PLUGIN"] = False
        tc.variables["PXR_BUILD_IMAGING"] = bool(self.options.use_imaging)
        tc.variables["PXR_ENABLE_MATERIALX_SUPPORT"] = True
        tc.variables["PXR_BUILD_OPENCOLORIO_PLUGIN"] = bool(self.options.use_imaging)
        tc.variables["PXR_BUILD_OPENIMAGEIO_PLUGIN"] = bool(self.options.use_imaging)
        tc.variables["PXR_BUILD_PRMAN_PLUGIN"] = False
        tc.variables["PXR_BUILD_TESTS"] = False
        tc.variables["PXR_BUILD_USD_IMAGING"] = bool(self.options.use_imaging)
        tc.variables["PXR_BUILD_USDVIEW"] = ((self.settings.os == "Linux") and bool(self.options.use_imaging))
        tc.variables["PXR_ENABLE_GL_SUPPORT"] = True
        tc.variables["PXR_ENABLE_HDF5_SUPPORT"] = True
        # tc.variables["PXR_ENABLE_OPENVDB_SUPPORT"] = False
        # tc.variables["PXR_ENABLE_OSL_SUPPORT"] = False
        tc.variables["PXR_ENABLE_PTEX_SUPPORT"] = True
        if self.options.with_python:
            tc.variables["PXR_ENABLE_PYTHON_SUPPORT"] = True
            tc.variables["PXR_USE_PYTHON_3"] = True
            tc.variables["Python3_FIND_STRATEGY"] = "LOCATION"
            tc.variables["Python3_ROOT_DIR"] = os.path.join(self.deps_cpp_info["cpython"].rootpath, "bin").replace("\\", "/")
        tc.variables["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        tc.variables["HDF5_USE_STATIC_LIBRARIES"] = not self.options["hdf5"].shared
        if self.options.use_imaging:
            tc.variables["OIIO_LOCATION"] = self.deps_cpp_info["openimageio"].rootpath.replace("\\", "/")
        tc.variables["TBB_tbb_LIBRARY"] = "TBB::tbb"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Linux":
            # fix shebangs
            python_shebang = "#!/usr/bin/env python3.7\n"
            bin_directory = os.path.join(self.package_folder, "bin")
            if os.path.exists(bin_directory):
                with chdir(self, bin_directory):
                    for filename in [entry for entry in os.listdir(".") if os.path.isfile(entry)]:
                        try:
                            with open(filename, "r") as infile:
                                lines = infile.readlines()
                            
                            if len(lines[0]) > 2 and lines[0].startswith("#!"):
                                lines[0] = python_shebang
                                with open(filename, "w") as outfile:
                                    outfile.writelines(lines)
                        except:
                            pass


    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.bindirs = ["lib", "bin"] # This will put "lib" folder in the path, which we need to find the plugins.
        self.cpp_info.defines = ["NOMINMAX", "YY_NO_UNISTD_H"]
        
        if self.settings.build_type == "Debug":
            self.cpp_info.defines.append("BUILD_OPTLEVEL_DEV")
        
        if not self.options.shared:
            self.cpp_info.defines.append("PXR_STATIC=1")
        if self.options.shared:
            if self.settings.os == "Windows":
                self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
                self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "lib"))
            else:
                self.runenv_info.prepend_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "bin"))
                self.runenv_info.prepend_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
        
        if self.options.with_python:
            self.buildenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "lib", "python"))
            self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "lib", "python"))
        self.runenv_info.prepend_path("PXR_PLUGINPATH_NAME", os.path.join(self.package_folder, "plugin", "usd"))
