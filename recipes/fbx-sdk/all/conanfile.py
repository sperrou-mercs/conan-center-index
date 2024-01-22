import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, collect_libs, download


class FbxSdkConan(ConanFile):
    name = "fbx-sdk"
    description = "free, easy-to-use, C++ software development platform and API toolkit that allows application and content vendors to transfer existing content into the FBX format with minimal effort"
    url = "https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-2"
    license = "autodesk"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": False
    }

    def config_options(self):
        if self.settings.os != "Windows":
            self.settings.remove("compiler")
    
    def validate(self):
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is the only supported toolchain on Windows")

    def requirements(self):
        self.requires("libxml2/[>=2.12 <3]")


    @property
    def _vs_year(self):
        if self.settings.compiler.version == 14:
            return "2015"
        elif self.settings.compiler.version == 15:
            return "2017"
        elif self.settings.compiler.version == 16:
            return "2019"
        elif self.settings.compiler.version == 17:
            return "2022"


    @property
    def _filename(self):
        version_id = self.version.replace(".", "")
        if self.settings.os == "Linux":
            return "fbx{version_id}_fbxsdk_linux.tar.gz"
        elif self.settings.os == "Windows":
            return f"fbx{version_id}_fbxsdk_vs{self._vs_year}_win.exe"

    def source(self):
        version_dir = self.version.replace(".", "-")
        if self.settings.os == "Linux":
            get(self, f"https://www.autodesk.com/content/dam/autodesk/www/adn/fbx/{version_dir}/{self._filename}")
        else:
            download(self, f"https://www.autodesk.com/content/dam/autodesk/www/adn/fbx/{version_dir}/{self._filename}", self._filename)

    def build(self):
        if self.settings.os == "Linux":
            version_id = self.version.replace(".", "")
            self.run(f"yes | ./fbx{version_id}_fbxsdk_linux {self.build_folder}")
        else:
            self.run(f"{self._filename} /S /D={self.build_folder}")

    def package(self):
        copy(self, "License.txt", self.build_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"))

        config = "debug" if self.settings.build_type == "Debug" else "release"
        arch = "x64" if self.settings.arch == "x86_64" else "arm64"
        if self.settings.os == "Linux":
            pattern = f"lib/gcc/x64/{config}/libfbxsdk.{"so" if self.options.shared else "a"}"
            copy(self, pattern, self.build_folder, os.path.join(self.package_folder, "lib"), False)
        else:
            lib_dir = f"lib/vs{self._vs_year}/{arch}/{config}"
            if self.options.shared:
                copy(self, f"{lib_dir}/libfbxsdk.lib", self.build_folder, os.path.join(self.package_folder, "lib"), False)
                copy(self, f"{lib_dir}/libfbxsdk.dll", self.build_folder, os.path.join(self.package_folder, "bin"), False)
            else:
                runtime = "mt" if self.settings.compiler.runtime == "MT" else "md"
                copy(self, f"{lib_dir}/libfbxsdk-{runtime}.lib", self.build_folder, os.path.join(self.package_folder, "lib"), False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
