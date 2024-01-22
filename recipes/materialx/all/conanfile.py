from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get

class MaterialXConan(ConanFile):
    name = "materialx"
    revision_mode = "scm"
    url = "https://www.materialx.org"
    description = "MaterialX is an open standard for transfer of rich material and look-development content between applications and renderers"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("glu/system")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MATERIALX_BUILD_PYTHON"] = False
        tc.variables["MATERIALX_BUILD_VIEWER"] = False
        tc.variables["MATERIALX_BUILD_DOCS"] = False
        tc.variables["MATERIALX_BUILD_TESTS"] = False
        tc.variables["MATERIALX_PYTHON_LTO"] = False
        tc.variables["MATERIALX_INSTALL_PYTHON"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # self.cpp_info.set_property("cmake_find_mode", "none")
        # self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "MaterialX"))
        self.cpp_info.set_property("cmake_file_name", "MaterialX")

        self.cpp_info.components["MaterialXCore"].set_property("cmake_target_name", "MaterialXCore")
        self.cpp_info.components["MaterialXCore"].libs = ["MaterialXCore"]

        self.cpp_info.components["MaterialXFormat"].set_property("cmake_target_name", "MaterialXFormat")
        self.cpp_info.components["MaterialXFormat"].libs = ["MaterialXFormat"]
        self.cpp_info.components["MaterialXFormat"].requires = ["MaterialXCore"]

        self.cpp_info.components["MaterialXGenGlsl"].set_property("cmake_target_name", "MaterialXGenGlsl")
        self.cpp_info.components["MaterialXGenGlsl"].libs = ["MaterialXGenGlsl"]
        self.cpp_info.components["MaterialXGenGlsl"].requires = ["MaterialXGenShader", "MaterialXCore"]

        self.cpp_info.components["MaterialXGenMdl"].set_property("cmake_target_name", "MaterialXGenMdl")
        self.cpp_info.components["MaterialXGenMdl"].libs = ["MaterialXGenMdl"]
        self.cpp_info.components["MaterialXGenMdl"].requires = ["MaterialXGenShader", "MaterialXCore"]

        self.cpp_info.components["MaterialXGenMsl"].set_property("cmake_target_name", "MaterialXGenMsl")
        self.cpp_info.components["MaterialXGenMsl"].libs = ["MaterialXGenMsl"]
        self.cpp_info.components["MaterialXGenMsl"].requires = ["MaterialXGenShader", "MaterialXCore"]

        self.cpp_info.components["MaterialXGenOsl"].set_property("cmake_target_name", "MaterialXGenOsl")
        self.cpp_info.components["MaterialXGenOsl"].libs = ["MaterialXGenOsl"]
        self.cpp_info.components["MaterialXGenOsl"].requires = ["MaterialXGenShader", "MaterialXCore"]

        self.cpp_info.components["MaterialXGenShader"].set_property("cmake_target_name", "MaterialXGenShader")
        self.cpp_info.components["MaterialXGenShader"].libs = ["MaterialXGenShader"]
        self.cpp_info.components["MaterialXGenShader"].requires = ["MaterialXCore", "MaterialXFormat"]

        self.cpp_info.components["MaterialXRender"].set_property("cmake_target_name", "MaterialXRender")
        self.cpp_info.components["MaterialXRender"].libs = ["MaterialXRender"]
        self.cpp_info.components["MaterialXRender"].requires = ["MaterialXGenShader"]

        self.cpp_info.components["MaterialXRenderGlsl"].set_property("cmake_target_name", "MaterialXRenderGlsl")
        self.cpp_info.components["MaterialXRenderGlsl"].libs = ["MaterialXRenderGlsl"]
        self.cpp_info.components["MaterialXRenderGlsl"].requires = ["MaterialXRenderHw", "MaterialXGenGlsl"]
        if self.settings.os == "Windows":
            self.cpp_info.components["MaterialXRenderGlsl"].system_libs.append("opengl32")

        self.cpp_info.components["MaterialXRenderHw"].set_property("cmake_target_name", "MaterialXRenderHw")
        self.cpp_info.components["MaterialXRenderHw"].libs = ["MaterialXRenderHw"]
        self.cpp_info.components["MaterialXRenderHw"].requires = ["MaterialXRender"]

        self.cpp_info.components["MaterialXRenderOsl"].set_property("cmake_target_name", "MaterialXRenderOsl")
        self.cpp_info.components["MaterialXRenderOsl"].libs = ["MaterialXRenderOsl"]
        self.cpp_info.components["MaterialXRenderOsl"].requires = ["MaterialXRender"]
