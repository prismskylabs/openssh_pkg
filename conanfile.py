import os
import fnmatch
import platform
from functools import total_ordering
from conans.errors import ConanInvalidConfiguration, ConanException
from conans import ConanFile, AutoToolsBuildEnvironment, tools

# This OpenSSH conanfile.py is done from openssl's conanfile.py taken from Conan Index


class OpenSSH_Conan(ConanFile):
    name = "openssh"
    version = "8.4p1"
    settings = "os", "compiler", "arch", "build_type"
    homepage = "https://github.com/openssh/openssh-portable"
    license = "Conanfile: MIT, OpenSSH itself: BSD."
    topics = ("conan", "openssh", "ssl", "tls", "encryption", "security")
    description = "A toolkit for Secure Shell remote access, transport and security"
    url = 'https://travis-ci.com/github/prismskylabs/openssh_pkg'
    options = {
            #"fPIC": [True, False],
              }
    default_options = {key: False for key in options.keys()}
    #default_options["fPIC"] = True
    _env_build = None
    _source_subfolder = "source_subfolder"
    exports_sources = ['patches/*']

    def config_options(self):
        pass

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_clangcl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _use_nmake(self):
        return self._is_clangcl or self._is_msvc

    @property
    def _full_version(self):
        return self.version

    def source(self):
        try:
            tools.get(**self.conan_data["sources"][self.version])
        except ConanException as ex:
            print("Got exception: " + str(ex))
            self.output.warn("Downloading OpenSSH from the mirror.")
            url = self.conan_data["sources"][self.version]["url"]
            #url = url.replace("https://www.openssl.org/source/",
            #                  "https://www.openssl.org/source/old/%s/" % self._full_version.base)
            tools.get(url, sha256=self.conan_data["sources"][self.version]["sha256"])
        extracted_folder = "openssh-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd


    def requirements(self):
        self.requires("openssl/1.1.1h")
        self.requires("zlib/1.2.11")

    @property
    def _target_prefix(self):
        return ""

    @property
    def _target(self):
        target = "conan-%s-%s-%s-%s-%s" % (self.settings.build_type,
                                           self.settings.os,
                                           self.settings.arch,
                                           self.settings.compiler,
                                           self.settings.compiler.version)
        if self._use_nmake:
            target = "VC-" + target  # VC- prefix is important as it's checked by Configure
        if self._is_mingw:
            target = "mingw-" + target
        return target


    @property
    def _targets(self):
        is_cygwin = self.settings.get_safe("os.subsystem") == "cygwin"
        is_1_0 = False
        return {
            "Linux-x86-clang": ("%slinux-generic32" % self._target_prefix) if is_1_0 else "i386-clang-linux",
            "Linux-x86_64-clang": ("%slinux-x86_64" % self._target_prefix) if is_1_0 else "86_64-clang-linux",
            "Linux-x86-*": ("%slinux-generic32" % self._target_prefix) if is_1_0 else "i386-generic32-linux",
            "Linux-x86_64-*": "x86_64-%s-linux" % self._target_prefix,
            "Linux-armv7-*": "armv7-gnueabi-linux",
            "Linux-armv7hf-*": "armv7hf-gnueabi-linux",
            "Linux-armv8-*": "aarch64-poky-linux",
            "Linux-mips-*": "mips32-generic-linux",
            "Linux-mips64-*": "mips64-generic-linux",
            "Macos-x86-*": "i386-cc-%sdarwin" % self._target_prefix,
            "Macos-x86_64-*": "x86_64-cc-%sdarwin64" % self._target_prefix,
           # Android targets are very broken, see https://github.com/openssl/openssl/issues/7398
            "Android-armv7-*": "armv7-generic32-linux",
            "Android-armv7hf-*": "armv7hf-generic32-linux",
            "Android-armv8-*": "aarch64-generic64-linux",
            "Android-x86-*": "i386-clang-linux",
            "Android-x86_64-*": "x86_64-clang-linux",
            "Windows-x86-gcc": "i386-generic32-Cygwin" if is_cygwin else "mingw",
            "Windows-x86_64-gcc": "Cygwin-x86_64" if is_cygwin else "mingw64",
            "Windows-*-gcc": "Cygwin-common" if is_cygwin else "mingw-common",
            "Windows-ia64-Visual Studio": "%sVC-WIN64I" % self._target_prefix,  # Itanium
            "Windows-x86-Visual Studio": "%sVC-WIN32" % self._target_prefix,
            "Windows-x86_64-Visual Studio": "%sVC-WIN64A" % self._target_prefix,
            "Windows-armv7-Visual Studio": "VC-WIN32-ARM",
            "Windows-armv8-Visual Studio": "VC-WIN64-ARM",
            "Windows-*-Visual Studio": "VC-noCE-common",
            "Windows-ia64-clang": "%sVC-WIN64I" % self._target_prefix,  # Itanium
            "Windows-x86-clang": "%sVC-WIN32" % self._target_prefix,
            "Windows-x86_64-clang": "%sVC-WIN64A" % self._target_prefix,
            "Windows-armv7-clang": "VC-WIN32-ARM",
            "Windows-armv8-clang": "VC-WIN64-ARM",
            "Windows-*-clang": "VC-noCE-common",
        }

    @property
    def _ancestor_target(self):
        query = "%s-%s-%s" % (self.settings.os, self.settings.arch, self.settings.compiler)
        ancestor = next((self._targets[i] for i in self._targets if fnmatch.fnmatch(query, i)), None)
        if not ancestor:
            raise ConanInvalidConfiguration("unsupported configuration: %s %s %s, "
                                            "please open an issue: "
                                            "https://github.com/conan-io/conan-center-index/issues. "
                                            "alternatively, set the CONAN_OPENSSL_CONFIGURATION environment variable "
                                            "into your conan profile "
                                            "(list of configurations can be found by running './Configure --help')." %
                                            (self.settings.os,
                                            self.settings.arch,
                                            self.settings.compiler))
        return ancestor

    def _tool(self, env_name, apple_name):
        if env_name in os.environ:
            return os.environ[env_name]
        if self.settings.compiler == "apple-clang":
            return getattr(tools.XCRun(self.settings), apple_name)
        return None

    def _patch_configure(self):
        # since _patch_makefile_org will replace binutils variables
        # use a more restricted regular expresion to prevent that Configure script trying to do it again
        #configure = os.path.join(self._source_subfolder, "Configure")
        #tools.replace_in_file(configure, r"s/^AR=\s*ar/AR= $ar/;", r"s/^AR=\s*ar\b/AR= $ar/;")
        pass

    def _get_env_build(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            if self.settings.compiler == "apple-clang":
                # add flags only if not already specified, avoid breaking Catalyst which needs very special flags
                flags = " ".join(self._env_build.flags)
                if "-arch" not in flags:
                    self._env_build.flags.append("-arch %s" % tools.to_apple_arch(self.settings.arch))
                if "-isysroot" not in flags:
                    self._env_build.flags.append("-isysroot %s" % tools.XCRun(self.settings).sdk_path)
                if self.settings.get_safe("os.version") and "-version-min=" not in flags and "-target" not in flags:
                    self._env_build.flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                              self.settings.os.version))
        return self._env_build

    @property
    def _configure_args(self):
        #opensshdir = self.options.opensshdir if self.options.opensshdir else os.path.join(self.package_folder, "res")
        prefix = '/usr/local/packages/prismconnect'
        #tools.unix_path(self.package_folder) if self._win_bash else self.package_folder
        #opensshdir = tools.unix_path(opensshdir) if self._win_bash else opensshdir
        args = [
          '--host=%s' % (self._ancestor_target),
          "--prefix=\"%s\"" % prefix,
          "--with-zlib",
          "--with-openssl",
          "--disable-libutil",
          "--without-libcrypt",
          "--disable-strip",
        ]

        if self.settings.compiler == "gcc": # Enable strip at linking
            args.append('--with-ldflags=-s')
            args.append('--with-ldflags-after=-s')


        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if activated and option_name not in ["fPIC"]:
                self.output.info("activated option: %s" % option_name)
                args.append(option_name.replace("_", "-"))
        return args

    def _run_make(self, targets=None, makefile=None, parallel=True, sudo=False):
        command = list()
        if sudo:
            command.append('sudo')

        command.append(self._make_program)

        if makefile:
            command.extend(["-f", makefile])
        if targets:
            command.extend(targets)
        if not self._use_nmake:
           command.append(("-j%s" % tools.cpu_count()) if parallel else "-j1")

        self.run(" ".join(command), win_bash=self._win_bash)

    @property
    def _perl(self):
       return "perl"

    @property
    def _nmake_makefile(self):
        return r"ms\ntdll.mak" #if self.options.shared else r"ms\nt.mak"

    def _make(self):
        with tools.chdir(self._source_subfolder):
            # workaround for clang-cl not producing .pdb files
            if self._is_clangcl:
                tools.save("ossh_static.pdb", "")
            args = " ".join(self._configure_args)
            self.output.info(self._configure_args)

            self.run('set;  ./configure {args}'.format(perl=self._perl, args=args), win_bash=self._win_bash)

            #self._patch_install_name()

            self._run_make()

    def _make_install(self):
        with tools.chdir(self._source_subfolder):
            # workaround for MinGW (https://github.com/openssl/openssl/issues/7653)
            if not os.path.isdir(os.path.join(self.package_folder, "bin")):
                os.makedirs(os.path.join(self.package_folder, "bin"))

            self._run_make(targets=["install-nokeys"], parallel=False, sudo=True)

    @property
    def _cc(self):
        if "CROSS_COMPILE" in os.environ:
            return "gcc"
        if "CC" in os.environ:
            return os.environ["CC"]
        if self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).find("clang")
        elif self.settings.compiler == "clang":
            return "clang"
        elif self.settings.compiler == "gcc":
            return "gcc"
        return "cc"

    def build(self):

        #autotools = AutoToolsBuildEnvironment(self)
        #autotools.configure()
        #autotools.make()

        with tools.vcvars(self.settings) if self._use_nmake else tools.no_op():
            env_vars = self._get_env_build().vars #{"PERL": self._perl}
            if self.settings.compiler == "apple-clang":
                xcrun = tools.XCRun(self.settings)
                env_vars["CROSS_SDK"] = os.path.basename(xcrun.sdk_path)
                env_vars["CROSS_TOP"] = os.path.dirname(os.path.dirname(xcrun.sdk_path))
            with tools.environment_append(env_vars):
                self._make()

    @property
    def _cross_building(self):
        if tools.cross_building(self.settings):
            if self.settings.os == tools.detected_os():
                if self.settings.arch == "x86" and tools.detected_architecture() == "x86_64":
                    return False
            return True
        return False

    @property
    def _win_bash(self):
        return tools.os_info.is_windows and \
               not self._use_nmake and \
               (self._is_mingw or self._cross_building)

    @property
    def _make_program(self):
        if self._use_nmake:
            return "nmake"
        make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which('mingw32-make'))
        make_program = tools.unix_path(make_program) if tools.os_info.is_windows else make_program
        if not make_program:
            raise Exception('could not find "make" executable. please set "CONAN_MAKE_PROGRAM" environment variable')
        return make_program

    def package(self):
        self.copy(src=self._source_subfolder, pattern="*LICENSE", dst="licenses")
        with tools.vcvars(self.settings) if self._use_nmake else tools.no_op():
            self._make_install()
        self.copy('ssh', dst='bin', src='/usr/local/packages/prismconnect/bin')
        self.copy('ssh-keygen', dst='bin', src='/usr/local/packages/prismconnect/bin')


    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenSSH"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSSH"
        self.cpp_info.bindirs = [ "bin" ]
