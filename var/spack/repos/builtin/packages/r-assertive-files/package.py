# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class RAssertiveFiles(RPackage):
    """Assertions to Check Properties of Files.

    A set of predicates and assertions for checking the properties of files and
    connections. This is mainly for use by other package developers who want to
    include run-time testing features in their own packages. End-users will
    usually want to use assertive directly."""

    cran = "assertive.files"

    version("0.0-2", sha256="be6adda6f18a0427449249e44c2deff4444a123244b16fe82c92f15d24faee0a")

    depends_on("r@3.0.0:", type=("build", "run"))
    depends_on("r-assertive-base@0.0-2:", type=("build", "run"))
    depends_on("r-assertive-numbers", type=("build", "run"))
