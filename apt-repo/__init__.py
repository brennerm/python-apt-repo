import bz2
import gzip
import lzma
import os
import re
import urllib.error
import urllib.request as request


def download_raw(url):
    return request.urlopen(url).read()


def download(url):
    return download_raw(url).decode('utf-8')


decompress = {
    '': lambda c: c,
    '.xz': lambda c: lzma.decompress(c),
    '.gz': lambda c: gzip.decompress(c),
    '.bzip2': lambda c: bz2.decompress(c)
}


def download_compressed(base_url):
    for suffix, method in decompress.items():
        url = base_url + suffix

        try:
            req = request.urlopen(url)
        except urllib.error.URLError:
            continue

        return method(req.read()).decode('utf-8')


def get_value(content, key):
    pattern = key + ': (.*)\n'
    match = re.search(pattern, content)
    try:
        return match.group(1)
    except AttributeError:
        raise KeyError(content, key)


class ReleaseFile:
    """Class that represents a Release file"""
    def __init__(self, content):
        self.__content = content.strip()

    @property
    def origin(self):
        return get_value(self.__content, 'Origin')

    @property
    def label(self):
        return get_value(self.__content, 'Label')

    @property
    def suite(self):
        return get_value(self.__content, 'Suite')

    @property
    def version(self):
        return get_value(self.__content, 'Version')

    @property
    def codename(self):
        return get_value(self.__content, 'Codename')

    @property
    def date(self):
        return get_value(self.__content, 'Date')

    @property
    def architectures(self):
        return get_value(self.__content, 'Architectures').split()

    @property
    def components(self):
        return get_value(self.__content, 'Components').split()

    @property
    def description(self):
        return get_value(self.__content, 'Description')


class PackagesFile:
    """"""
    def __init__(self, content):
        self.__content = content.strip()

    @property
    def packages(self):
        packages = []
        for package_content in self.__content.split('\n\n'):
            if not package_content:
                continue

            packages.append(BinaryPackage(package_content))

        return packages


class BinaryPackage:
    def __init__(self, content):
        self.__content = content.strip()
        
    @property
    def package(self):
        return get_value(self.__content, 'Package')

    @property
    def version(self):
        return get_value(self.__content, 'Version')


class APTRepository:
    def __init__(self, url, dist, components):
        self.__url = url
        self.__dist = dist
        self.__components = components

    @property
    def components(self):
        return self.__components

    @property
    def all_components(self):
        return self.release_file.components

    @property
    def release_file(self):
        url = os.path.join(
            self.__url,
            'dists',
            self.__dist,
            'Release'
        )

        release_content = download(url)

        return ReleaseFile(release_content)

    @property
    def packages(self, arch='amd64'):
        packages = []
        for component in self.__components:
            packages.extend(self.get_binary_packages_by_component(component, arch))

        return packages

    def get_binary_packages_by_component(self, component, arch='amd64'):
        url = os.path.join(
            self.__url,
            'dists',
            self.__dist,
            component,
            'binary-' + arch,
            'Packages'
        )

        packages_file = download_compressed(url)

        return PackagesFile(packages_file).packages

    def get_packages_by_name(self, name):
        all_binary_packages = self.packages
        packages = []

        for package in all_binary_packages:
            if package.package == name:
                packages.append(package)

        return packages


class APTSources:
    def __init__(self, repositories):
        self.__repositories = repositories

    @property
    def packages(self):
        packages = []

        for repo in self.__repositories:
            packages.extend(repo.packages)

        return packages

    def get_packages_by_name(self, name):
        packages = []

        for repo in self.__repositories:
            packages.extend(repo.get_packages_by_name(name))

        return packages
