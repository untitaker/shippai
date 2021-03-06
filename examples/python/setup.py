from setuptools import setup, find_packages


def build_native(spec):
    build = spec.add_external_build(
        # you might want to adapt this line to use --release
        cmd=['cargo', 'build'],
        path='./rust/'
    )

    spec.add_cffi_module(
        module_path='shippai_example._native',
        dylib=lambda: build.find_dylib(
            # also maybe use the release folder here
            'shippai_example', in_path='target/debug/'),
        header_filename='native.h',
        rtld_flags=['NODELETE']
    )


setup(
    name='shippai_example',
    version='0.1.0',
    author='Markus Unterwaditzer',
    author_email='markus-python@unterwaditzer.net',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    license='MIT',
    classifiers=['License :: OSI Approved :: MIT License'],
    setup_requires=['milksnake'],
    install_requires=['shippai'],
    milksnake_tasks=[build_native]
)
