import os
import re
import sys
import errno
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.build_ext import build_ext

#-----------------------------------------------------------------------------
# Flags and default values.
#-----------------------------------------------------------------------------

PACKAGE = 'pyhll'

cmdclass = {}
extensions = []
extension_kwargs = {}


# try to find cython
try:
    from Cython.Distutils import build_ext as build_ext_c
    cython_installed = True
except ImportError:
    cython_installed = False


# current location
here = os.path.abspath(os.path.dirname(__file__))


def exec_process(cmdline, silent=True, input=None, **kwargs):
    """Execute a subprocess and returns the returncode, stdout buffer and stderr buffer.
    Optionally prints stdout and stderr while running."""
    try:
        sub = subprocess.Popen(args=cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        stdout, stderr = sub.communicate(input=input)
        returncode = sub.returncode
        if not silent:
            sys.stdout.write(stdout)
            sys.stderr.write(stderr)
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise RuntimeError('"%s" is not present on this system' % cmdline[0])
        else:
            raise
    if returncode != 0:
        raise RuntimeError('Got return value %d while executing "%s", stderr output was:\n%s' % (returncode, " ".join(cmdline), stderr.decode("utf-8").rstrip("\n")))
    return stdout


#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------

class CheckSDist(sdist):
    """Custom sdist that ensures Cython has compiled all pyx files to c."""

    def initialize_options(self):
        sdist.initialize_options(self)
        self._pyxfiles = []
        for root, dirs, files in os.walk(PACKAGE):
            for f in files:
                if f.endswith('.pyx'):
                    self._pyxfiles.append(os.path.join(root, f))

    def run(self):
        if 'cython' in cmdclass:
            self.run_command('cython')
        else:
            for pyxfile in self._pyxfiles:
                cfile = pyxfile[:-3] + 'c'
                msg = "C-source file '%s' not found."%(cfile)+\
                " Run 'setup.py cython' before sdist."
                assert os.path.isfile(cfile), msg
        sdist.run(self)

cmdclass['sdist'] = CheckSDist


class BaseMurmurMixin:

    murmur_dir = os.path.join(here, 'deps', 'murmurhash')

    def build_murmur(self):
        cflags = '-fPIC'
        env = os.environ.copy()
        env['CPPFLAGS'] = ' '.join(x for x in (cflags, env.get('CPPFLAGS', None)) if x)
        exec_process(['sh', 'autogen.sh'], cwd=self.murmur_dir, env=env, silent=True)
        exec_process(['./configure'], cwd=self.murmur_dir, env=env, silent=True)
        exec_process(['make'], cwd=self.murmur_dir, env=env, silent=False)

    def prepare_extensions(self):
        self.murmur_lib = os.path.join(self.murmur_dir, '.libs', 'libMurmurHash3.a')
        if not os.path.exists(os.path.join(self.murmur_dir, '.libs')):
            self.build_murmur()
        self.extensions[0].extra_objects.extend([self.murmur_lib])
        self.compiler.add_include_dir(self.murmur_lib)


if cython_installed:

    class CythonCommand(build_ext_c):
        """Custom distutils command subclassed from Cython.Distutils.build_ext
        to compile pyx->c, and stop there. All this does is override the
        C-compile method build_extension() with a no-op."""

        description = "Compile Cython sources to C"

        def build_extension(self, ext):
            pass


    class MurmurMixin(BaseMurmurMixin):

        def build_extensions(self):
            self.prepare_extensions()
            build_ext_c.build_extensions(self)


    class zbuild_ext(MurmurMixin, build_ext_c):

        def run(self):
            from distutils.command.build_ext import build_ext as _build_ext
            return _build_ext.run(self)

    cmdclass['cython'] = CythonCommand
    cmdclass['build_ext'] = zbuild_ext

else:

    class CheckingBuildExt(BaseMurmurMixin, build_ext):
        """Subclass build_ext to get clearer report if Cython is neccessary."""

        def check_cython_extensions(self, extensions):
            for ext in extensions:
                for src in ext.sources:
                    msg = "Cython-generated file '%s' not found." % src
                    assert os.path.exists(src), msg

        def build_extensions(self):
            self.prepare_extensions()
            self.check_cython_extensions(self.extensions)
            self.check_extensions_list(self.extensions)

            for ext in self.extensions:
                self.build_extension(ext)

    cmdclass['build_ext'] = CheckingBuildExt


#-----------------------------------------------------------------------------
# Extensions
#-----------------------------------------------------------------------------


suffix = '.pyx' if cython_installed else '.c'


def source_extension(name):
    parts = name.split('.')
    parts[-1] = parts[-1] + suffix
    return os.path.join(PACKAGE, *parts)


def prepare_sources(sources):
    def to_string(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s
    return [to_string(source) for source in sources]


modules = {
    'hll': dict(
        include_dirs=[os.path.join(here, 'src')],
        sources=[
            source_extension('hll'),
            os.path.join(here, 'src', 'hll.c'),
            os.path.join(here, 'src', 'hll_constants.c'),
        ],
        extra_compile_args=['-std=c99'],
    ),
}

# collect extensions
for module, kwargs in modules.items():
    kwargs = dict(extension_kwargs, **kwargs)
    kwargs.setdefault('sources', [source_extension(module)])
    kwargs['sources'] = prepare_sources(kwargs['sources'])
    ext = Extension('{0}.{1}'.format(PACKAGE, module), **kwargs)
    if suffix == '.pyx' and ext.sources[0].endswith('.c'):
        # undo setuptools stupidly clobbering cython sources:
        ext.sources = kwargs['sources']
    extensions.append(ext)


#-----------------------------------------------------------------------------
# Description, version and other meta information.
#-----------------------------------------------------------------------------

re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
re_vers = re.compile(r'VERSION\s*=\s*\((.*?)\)')
re_doc = re.compile(r'^"""(.+?)"""')
rq = lambda s: s.strip("\"'")


def add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, rq(attr_value)),)


def add_version(m):
    v = list(map(rq, m.groups()[0].split(', ')))
    return (('VERSION', '.'.join(v[0:3]) + ''.join(v[3:])),)


def add_doc(m):
    return (('doc', m.groups()[0]),)

pats = {re_meta: add_default,
        re_vers: add_version,
        re_doc: add_doc}
meta_fh = open(os.path.join(here, '{0}/__init__.py'.format(PACKAGE)))
try:
    meta = {}
    for line in meta_fh:
        if line.strip() == '# -eof meta-':
            break
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()


#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

setup(
    name=PACKAGE,
    version=meta['VERSION'],
    description=meta['doc'],
    author=meta['author'],
    author_email=meta['contact'],
    url=meta['homepage'],
    long_description=README + '\n\n' + CHANGES,
    keywords='thrift soa',
    license='BSD',
    cmdclass=cmdclass,
    ext_modules=extensions,
    packages=find_packages(),
    install_requires=[],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
    ],
)
