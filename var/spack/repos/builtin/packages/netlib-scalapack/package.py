# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import sys

from spack.package import *


class ScalapackBase(CMakePackage):
    """Base class for building ScaLAPACK, shared with the AMD optimized version
    of the library in the 'amdscalapack' package.
    """

    variant("shared", default=True, description="Build the shared library version")
    variant("pic", default=False, description="Build position independent code")

    provides("scalapack")

    depends_on("mpi")
    depends_on("lapack")
    depends_on("blas")
    depends_on("cmake", when="@2.0.0:", type="build")

    # See: https://github.com/Reference-ScaLAPACK/scalapack/issues/9
    patch("cmake_fortran_mangle.patch", when="@2.0.2:2.0")
    # See: https://github.com/Reference-ScaLAPACK/scalapack/pull/10
    patch("mpi2-compatibility.patch", when="@2.0.2:2.0")
    # See: https://github.com/Reference-ScaLAPACK/scalapack/pull/16
    patch("int_overflow.patch", when="@2.0.0:2.1.0")
    # See: https://github.com/Reference-ScaLAPACK/scalapack/pull/23
    patch("gcc10-compatibility.patch", when="@2.0.0:2.2.0")
    # See: https://github.com/Reference-ScaLAPACK/scalapack/pull/57
    patch(
        "https://github.com/Reference-ScaLAPACK/scalapack/commit/d4d0066c041cf19a23f8b3aa62fbcf5f0a33c166.patch?full_index=1",
        sha256="072b006e485f0ca4cba56096912a986e4d3da73aae51c2205928aa5eb842cefd",
        when="@2.2.0",
    )
    # From Homebrew, integrated @upstream in different form over multiple commits
    patch("fix-build-macos.patch", when="@2.2.0")

    def flag_handler(self, name, flags):
        if name == "cflags":
            if self.spec.satisfies("%cce"):
                flags.append("-Wno-error=implicit-function-declaration")
            if self.spec.satisfies("%gcc@14:"):
                # https://bugzilla.redhat.com/show_bug.cgi?id=2178710
                flags.append("-std=gnu89")
        elif name == "fflags":
            if self.spec.satisfies("%cce"):
                flags.append("-hnopattern")
        return (flags, None, None)

    @property
    def libs(self):
        # Note that the default will be to search
        # for 'libnetlib-scalapack.<suffix>'
        shared = True if "+shared" in self.spec else False
        return find_libraries("libscalapack", root=self.prefix, shared=shared, recursive=True)

    def cmake_args(self):
        spec = self.spec

        options = [
            "-DBUILD_SHARED_LIBS:BOOL=%s" % ("ON" if "+shared" in spec else "OFF"),
            "-DBUILD_STATIC_LIBS:BOOL=%s" % ("OFF" if "+shared" in spec else "ON"),
        ]

        # Make sure we use Spack's Lapack:
        blas = spec["blas"].libs
        lapack = spec["lapack"].libs
        options.extend(
            [
                "-DLAPACK_FOUND=true",
                "-DLAPACK_INCLUDE_DIRS=%s" % spec["lapack"].prefix.include,
                "-DLAPACK_LIBRARIES=%s" % (lapack.joined(";")),
                "-DBLAS_LIBRARIES=%s" % (blas.joined(";")),
            ]
        )

        c_flags = []
        if "+pic" in spec:
            c_flags.append(self.compiler.cc_pic_flag)
            options.append("-DCMAKE_Fortran_FLAGS=%s" % self.compiler.fc_pic_flag)

        # Work around errors of the form:
        #   error: implicit declaration of function 'BI_smvcopy' is
        #   invalid in C99 [-Werror,-Wimplicit-function-declaration]
        if (
            spec.satisfies("%clang")
            or spec.satisfies("%apple-clang")
            or spec.satisfies("%oneapi")
            or spec.satisfies("%arm")
            or spec.satisfies("%cce")
            or spec.satisfies("%rocmcc")
        ):
            c_flags.append("-Wno-error=implicit-function-declaration")

        options.append(self.define("CMAKE_C_FLAGS", " ".join(c_flags)))

        return options

    @run_after("install")
    def fix_darwin_install(self):
        # The shared libraries are not installed correctly on Darwin:
        if (sys.platform == "darwin") and ("+shared" in self.spec):
            fix_darwin_install_name(self.spec.prefix.lib)


class NetlibScalapack(ScalapackBase):
    """ScaLAPACK is a library of high-performance linear algebra routines for
    parallel distributed memory machines
    """

    homepage = "https://www.netlib.org/scalapack/"
    url = "https://github.com/Reference-ScaLAPACK/scalapack/archive/refs/tags/v2.2.2.tar.gz"
    git = "https://github.com/Reference-ScaLAPACK/scalapack"
    tags = ["e4s"]

    maintainers("etiennemlb")

    license("BSD-3-Clause-Open-MPI")

    version("2.2.2", sha256="a2f0c9180a210bf7ffe126c9cb81099cf337da1a7120ddb4cbe4894eb7b7d022")
    version("2.2.0", sha256="8862fc9673acf5f87a474aaa71cd74ae27e9bbeee475dbd7292cec5b8bcbdcf3")
    version("2.1.0", sha256="f03fda720a152030b582a237f8387014da878b84cbd43c568390e9f05d24617f")
    version("2.0.2", sha256="0c74aeae690fe5ee4db7926f49c5d0bb69ce09eea75beb915e00bba07530395c")
    version("2.0.1", sha256="a9b34278d4e10b40cbe084c6d87d09af8845e874250719bfbbc497b2a88bfde1")
    version("2.0.0", sha256="e51fbd9c3ef3a0dbd81385b868e2355900148eea689bf915c5383d72daf73114")
    version("master", branch="master")

    depends_on("c", type="build")  # generated
    depends_on("fortran", type="build")  # generated
    # versions before 2.0.0 are not using cmake and requires blacs as
    # a separated package

    def url_for_version(self, version):
        if self.spec.satisfies("@2.2:"):
            return super().url_for_version(version)
        url_fmt = "https://www.netlib.org/scalapack/scalapack-{0}.tgz"
        return url_fmt.format(version)
