# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class PyOgb(PythonPackage):
    """The Open Graph Benchmark (OGB) is a collection of benchmark datasets, data
    loaders, and evaluators for graph machine learning. Datasets cover a variety of
    graph machine learning tasks and real-world applications. The OGB data loaders
    are fully compatible with popular graph deep learning frameworks, including
    PyTorch Geometric and Deep Graph Library (DGL). They provide automatic dataset
    downloading, standardized dataset splits, and unified performance evaluation.
    """

    homepage = "https://github.com/snap-stanford/ogb"
    pypi = "ogb/ogb-1.3.5.tar.gz"

    maintainers("meyersbs")

    license("MIT")

    version("1.3.6", sha256="ce90418a0e3206483187aa7b7ecac1a2c5d85b3b99aceedb807138ee43115914")
    version("1.3.5", sha256="ac958094ac3019822e742155b82cb2bf02830aa72a4264ba9ee09b288f0c080c")

    depends_on("py-setuptools", type="build")
    depends_on("py-torch@1.6.0:", type=("build", "run"))
    depends_on("py-numpy@1.16.0:", type=("build", "run"))
    depends_on("py-tqdm@4.29.0:", type=("build", "run"))
    depends_on("py-scikit-learn@0.20.0:", type=("build", "run"))
    depends_on("py-pandas@0.24.0:", type=("build", "run"))
    depends_on("py-six@1.12.0:", type=("build", "run"))
    depends_on("py-urllib3@1.24.0:", type=("build", "run"))
    depends_on("py-outdated@0.2.0:", type=("build", "run"))
