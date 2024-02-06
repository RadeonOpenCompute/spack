# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import sys

from spack.package import *


def _parse_float(val):
    try:
        return float(val) > 0.0
    except ValueError:
        return False


class NaluWind(CMakePackage, CudaPackage):
    """Nalu-Wind: Wind energy focused variant of Nalu."""

    homepage = "https://nalu-wind.readthedocs.io"
    git = "https://github.com/exawind/nalu-wind.git"

    maintainers("jrood-nrel", "psakievich")

    tags = ["ecp", "ecp-apps"]

    version("master", branch="master")

    variant("pic", default=True, description="Position independent code")
    variant(
        "abs_tol",
        default=1.0e-15,
        values=_parse_float,
        description="Absolute tolerance for regression tests",
    )
    variant(
        "rel_tol",
        default=1.0e-12,
        values=_parse_float,
        description="Relative tolerance for regression tests",
    )
    variant("openfast", default=False, description="Compile with OpenFAST support")
    variant("tioga", default=False, description="Compile with Tioga support")
    variant("hypre", default=True, description="Compile with Hypre support")
    variant("trilinos-solvers", default=True, description="Compile with Trilinos Solvers support")
    variant("catalyst", default=False, description="Compile with Catalyst support")
    variant("fftw", default=False, description="Compile with FFTW support")
    variant("boost", default=False, description="Enable Boost integration")
    variant("wind-utils", default=False, description="Build wind-utils")

    depends_on("mpi")
    depends_on("yaml-cpp@0.5.3:")
    depends_on(
        "trilinos@13:"
        "+exodus+tpetra+zoltan+stk+boost"
        "~superlu-dist~superlu+hdf5+shards~hypre+gtest"
    )
    depends_on("trilinos~cuda~wrapper", when="~cuda")
    # Cannot build Trilinos as a shared library with STK on Darwin
    # https://github.com/trilinos/Trilinos/issues/2994
    depends_on("trilinos~shared", when=(sys.platform == "darwin"))
    depends_on("openfast@2.6.0: +cxx", when="+openfast")
    depends_on("tioga@master:", when="+tioga")
    depends_on("hypre@2.18.2: ~int64+mpi~superlu-dist", when="+hypre")
    depends_on("trilinos+muelu+belos+amesos2+ifpack2", when="+trilinos-solvers")
    conflicts(
        "~hypre~trilinos-solvers",
        msg="nalu-wind: Must enable at least one of the linear-solvers: hypre or trilinos-solvers",
    )
    depends_on("kokkos-nvcc-wrapper", type="build", when="+cuda")
    for _arch in CudaPackage.cuda_arch_values:
        depends_on(
            "trilinos~shared+cuda+cuda_rdc+wrapper cuda_arch={0}".format(_arch),
            when="+cuda cuda_arch={0}".format(_arch),
        )
        depends_on(
            "hypre@develop +mpi+cuda~int64~superlu-dist cuda_arch={0}".format(_arch),
            when="+hypre+cuda cuda_arch={0}".format(_arch),
        )
    depends_on("trilinos-catalyst-ioss-adapter", when="+catalyst")
    depends_on("fftw+mpi", when="+fftw")
    depends_on("nccmp")
    # indirect dependency needed to make original concretizer work
    depends_on("netcdf-c+parallel-netcdf")
    depends_on("boost +filesystem +iostreams cxxstd=14", when="+boost")

    def cmake_args(self):
        spec = self.spec

        args = [
            self.define_from_variant("CMAKE_POSITION_INDEPENDENT_CODE", "pic"),
            self.define("CMAKE_CXX_COMPILER", spec["mpi"].mpicxx),
            self.define("CMAKE_Fortran_COMPILER", spec["mpi"].mpifc),
            self.define("Trilinos_DIR", spec["trilinos"].prefix),
            self.define("YAML_DIR", spec["yaml-cpp"].prefix),
            self.define_from_variant("ENABLE_CUDA", "cuda"),
            self.define_from_variant("ENABLE_WIND_UTILS", "wind-utils"),
            self.define_from_variant("ENABLE_BOOST", "boost"),
        ]

        args.append(self.define_from_variant("ENABLE_OPENFAST", "openfast"))
        if "+openfast" in spec:
            args.append(self.define("OpenFAST_DIR", spec["openfast"].prefix))

        args.append(self.define_from_variant("ENABLE_TIOGA", "tioga"))
        if "+tioga" in spec:
            args.append(self.define("TIOGA_DIR", spec["tioga"].prefix))

        args.append(self.define_from_variant("ENABLE_HYPRE", "hypre"))
        if "+hypre" in spec:
            args.append(self.define("HYPRE_DIR", spec["hypre"].prefix))

        args.append(self.define_from_variant("ENABLE_TRILINOS_SOLVERS", "trilinos-solvers"))
        args.append(self.define_from_variant("ENABLE_PARAVIEW_CATALYST", "catalyst"))
        if "+catalyst" in spec:
            args.append(
                self.define(
                    "PARAVIEW_CATALYST_INSTALL_PATH", spec["trilinos-catalyst-ioss-adapter"].prefix
                )
            )

        args.append(self.define_from_variant("ENABLE_FFTW", "fftw"))
        if "+fftw" in spec:
            args.append(self.define("FFTW_DIR", spec["fftw"].prefix))

        args.append(self.define("ENABLE_TESTS", self.run_tests))
        if self.run_tests:
            args.extend(
                [
                    self.define("TEST_TOLERANCE", spec.variants["abs_tol"].value),
                    self.define("TEST_REL_TOL", spec.variants["rel_tol"].value),
                ]
            )

        if "darwin" in spec.architecture:
            args.append(self.define("CMAKE_MACOSX_RPATH", "ON"))

        return args

    @run_before("cmake")
    def add_submodules(self):
        if self.run_tests or "+wind-utils" in self.spec:
            git = which("git")
            git("submodule", "update", "--init", "--recursive")
