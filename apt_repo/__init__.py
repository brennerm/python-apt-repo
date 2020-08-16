import bz2
import gzip
import lzma
import os
import posixpath
import re
import urllib.error
import urllib.request as request


def __download_raw(url):
    """
    Downloads a binary file

    # Arguments
    url (str): URL to file
    """
    return request.urlopen(url).read()


def _download(url):
    """
    Downloads a UTF-8 encoded file

    # Arguments
    url (str): URL to file
    """
    return __download_raw(url).decode('utf-8')


def _download_compressed(base_url):
    """
    Downloads a compressed file

    It tries out multiple compression algorithms by iterating through the according file suffixes.

    # Arguments
    url (str): URL to file
    """
    decompress = {
        '': lambda c: c,
        '.xz': lambda c: lzma.decompress(c),
        '.gz': lambda c: gzip.decompress(c),
        '.bzip2': lambda c: bz2.decompress(c)
    }

    for suffix, method in decompress.items():
        url = base_url + suffix

        try:
            req = request.urlopen(url)
        except urllib.error.URLError:
            continue

        return method(req.read()).decode('utf-8')


def _get_value(content, key):
    """
    Extracts a value from a Packages,Release file

    # Arguments
    content (str): the content of the Packages/Release file
    key (str): the key to return the value for
    """
    pattern = key + ': (.*)\n'
    match = re.search(pattern, content)
    try:
        return match.group(1)
    except AttributeError:
        raise KeyError(content, key)


class ReleaseFile:
    """
    Class that represents a Release file

    # Arguments
    content (str): the content of the Release file
    """
    def __init__(self, content):
        self.__content = content.strip()

    @property
    def origin(self):
        return _get_value(self.__content, 'Origin')

    @property
    def label(self):
        return _get_value(self.__content, 'Label')

    @property
    def suite(self):
        return _get_value(self.__content, 'Suite')

    @property
    def version(self):
        return _get_value(self.__content, 'Version')

    @property
    def codename(self):
        return _get_value(self.__content, 'Codename')

    @property
    def date(self):
        return _get_value(self.__content, 'Date')

    @property
    def architectures(self):
        return _get_value(self.__content, 'Architectures').split()

    @property
    def components(self):
        return _get_value(self.__content, 'Components').split()

    @property
    def description(self):
        return _get_value(self.__content, 'Description')


class PackagesFile:
    """
    Class that represents a Packages file

    # Arguments
    content (str): the content of the Packages file
    """
    def __init__(self, content):
        self.__content = content.strip()

    @property
    def packages(self):
        """Returns all binary packages in this Packages files"""
        packages = []
        for package_content in self.__content.split('\n\n'):
            if not package_content:
                continue

            packages.append(BinaryPackage(package_content))

        return packages


class BinaryPackage:
    """
    Class that represents a binary Debian package


    # Arguments
    content (str): the section of the Packages file for this specific package
    """
    def __init__(self, content):
        self.__content = content.strip()

    @property
    def package(self):
        return _get_value(self.__content, 'Package')

    @property
    def version(self):
        return _get_value(self.__content, 'Version')

    @property
    def filename(self):
        return _get_value(self.__content, 'Filename')

    @property
    def maintainer(self):
        try:
            return _get_value(self.__content, 'Maintainer')
        except KeyError:
            return None

    @property
    def original_maintainer(self):
        try:
            return _get_value(self.__content, 'Original-Maintainer')
        except KeyError:
            return None

    @property
    def architecture(self):
        try:
            return _get_value(self.__content, 'Architecture')
        except KeyError:
            return None

    @property
    def multi_arch(self):
        try:
            return _get_value(self.__content, 'Multi-Arch')
        except KeyError:
            return None

    @property
    def homepage(self):
        try:
            return _get_value(self.__content, 'Homepage')
        except KeyError:
            return None

    @property
    def origin(self):
        try:
            return _get_value(self.__content, 'Origin')
        except KeyError:
            return None

    @property
    def priority(self):
        try:
            return _get_value(self.__content, 'Priority')
        except KeyError:
            return None

    @property
    def section(self):
        try:
            return _get_value(self.__content, 'Section')
        except KeyError:
            return None

    @property
    def depends(self):
        try:
            field = _get_value(self.__content, 'Depends')
        except KeyError:
            return None

        if field:
            depends = [d.strip() for d in field.split(',')]
        else:
            depends = []
        return depends

    @property
    def replaces(self):
        try:
            field = _get_value(self.__content, 'Replaces')
        except KeyError:
            return None

        if field:
            replaces = [d.strip() for d in field.split(',')]
        else:
            replaces = []
        return replaces

    @property
    def breaks(self):
        try:
            field = _get_value(self.__content, 'Breaks')
        except KeyError:
            return None

        if field:
            breaks = [d.strip() for d in field.split(',')]
        else:
            breaks = []
        return breaks

    @property
    def recommends(self):
        try:
            field = _get_value(self.__content, 'Recommends')
        except KeyError:
            return None

        if field:
            recommends = [d.strip() for d in field.split(',')]
        else:
            recommends = []
        return recommends

    @property
    def suggests(self):
        try:
            field = _get_value(self.__content, 'Suggests')
        except KeyError:
            return None

        if field:
            suggests = [d.strip() for d in field.split(',')]
        else:
            suggests = []
        return suggests

    @property
    def conflicts(self):
        try:
            field = _get_value(self.__content, 'Conflicts')
        except KeyError:
            return None

        if field:
            conflicts = [d.strip() for d in field.split(',')]
        else:
            conflicts = []
        return conflicts

    @property
    def installed_size(self):
        try:
            return _get_value(self.__content, 'Installed-Size')
        except KeyError:
            return None

    @property
    def size(self):
        try:
            return _get_value(self.__content, 'Size')
        except KeyError:
            return None

    @property
    def md5(self):
        try:
            return _get_value(self.__content, 'MD5Sum')
        except KeyError:
            return None

    @property
    def sha1(self):
        try:
            return _get_value(self.__content, 'SHA1')
        except KeyError:
            return None

    @property
    def sha256(self):
        try:
            return _get_value(self.__content, 'SHA256')
        except KeyError:
            return None

    @property
    def description(self):
        try:
            return _get_value(self.__content, 'Description')
        except KeyError:
            return None

    @property
    def description_md5(self):
        try:
            return _get_value(self.__content, 'Description-md5')
        except KeyError:
            return None

    @property
    def built_using(self):
        try:
            return _get_value(self.__content, 'Built-Using')
        except KeyError:
            return None

    @property
    def source(self):
        try:
            return _get_value(self.__content, 'Source')
        except KeyError:
            return None

    @property
    def task(self):
        try:
            return _get_value(self.__content, 'Task')
        except KeyError:
            return None

    @property
    def supported(self):
        try:
            return _get_value(self.__content, 'Supported')
        except KeyError:
            return None

class APTRepository:
    """
    Class that represents a single APT repository

    # Arguments
    url (str): the base URL of the repository
    dist (str): the target distribution
    components (list): the target components

    # Examples
    ```python
    APTRepository('http://archive.ubuntu.com/ubuntu', 'bionic', 'main')
    APTRepository('https://pkg.jenkins.io/debian/', 'binary')
    ```
    """
    def __init__(self, url, dist, components=[]):
        self.url = url
        self.dist = dist
        self.components = components

    def __getitem__(self, item):
        return self.get_packages_by_name(item)

    @staticmethod
    def from_sources_list_entry(entry):
        """
        Instantiates a new APTRepository object out of a sources.list file entry

        # Examples
        ```python
        APTRepository.from_sources_list_entry('deb http://archive.ubuntu.com/ubuntu bionic main')
        ```
        """
        split_entry = entry.split()

        url = split_entry[1]
        dist = split_entry[2]
        try:
            components = split_entry[3:]
        except IndexError:
            # we assume that it is a flat repo https://wiki.debian.org/DebianRepository/Format#Flat_Repository_Format
            components = []

        return APTRepository(url, dist, components)

    @property
    def all_components(self):
        """Returns the all components of this repository"""
        return self.release_file.components

    @property
    def release_file(self):
        """Returns the Release file of this repository"""
        url = posixpath.join(
            self.url,
            'dists',
            self.dist,
            'Release'
        )

        release_content = _download(url)

        return ReleaseFile(release_content)

    @property
    def packages(self, arch='amd64'):
        """
        Returns all binary packages of this repository

        # Arguments
        arch (str): the architecture to return packages for, default: 'amd64'
        """
        packages = []
        if len(self.components) == 0:
            packages.extend(self.get_binary_packages_by_component(None, arch))
        for component in self.components:
            packages.extend(self.get_binary_packages_by_component(component, arch))

        return packages

    def get_binary_packages_by_component(self, component, arch='amd64'):
        """
        Returns all binary packages of this repository for a given component

        # Arguments
        component (str): the component to return packages for
        arch (str): the architecture to return packages for, default: 'amd64'
        """
        if component is None:
            url = posixpath.join(
                self.url,
                self.dist,
                'Packages')
        else:
            url = posixpath.join(
                self.url,
                'dists',
                self.dist,
                component,
                'binary-' + arch,
                'Packages'
        )

        packages_file = _download_compressed(url)

        return PackagesFile(packages_file).packages

    def get_package(self, name, version):
        """
        Returns a single binary package

        # Arguments
        name (str): name of the package
        version (str): version of the package
        """
        for package in self.packages:
            if package.package == name and package.version == version:
                return package

        raise KeyError(name, version)

    def get_package_url(self, name, version):
        """
        Returns the URL for a single binary package

        # Arguments
        name (str): name of the package
        version (str): version of the package
        """
        package = self.get_package(name, version)

        return posixpath.join(self.url, package.filename)

    def get_packages_by_name(self, name):
        """
        Returns the list of available packages (and it's available versions) for a specific package name

        # Arguments
        name (str): name of the package
        """

        packages = []

        for package in self.packages:
            if package.package == name:
                packages.append(package)

        return packages


class APTSources:
    """
    Class that represents a collection of APT repositories

    # Arguments
    repositories (list): list of APTRepository objects
    """
    def __init__(self, repositories):
        self.__repositories = repositories

    def __getitem__(self, item):
        return self.get_packages_by_name(item)

    @property
    def packages(self):
        """Returns all binary packages of all APT repositories"""
        packages = []

        for repo in self.__repositories:
            packages.extend(repo.packages)

        return packages

    def get_package(self, name, version):
        """
        Returns a single binary package

        # Arguments
        name (str): the name of the package
        version (str): the version of the package
        """
        for repo in self.__repositories:
            try:
                return repo.get_package(name, version)
            except KeyError:
                pass

        raise KeyError(name, version)

    def get_package_url(self, name, version):
        """
        Returns the URL of a single binary package

        # Arguments
        name (str): the name of the package
        version (str): the version of the package
        """
        for repo in self.__repositories:
            try:
                return repo.get_package_url(name, version)
            except KeyError:
                pass

        raise KeyError(name, version)

    def get_packages_by_name(self, name):
        """
        Returns the list of available packages (and it's available versions) for a specific package name

        # Arguments
        name (str): name of the package
        """

        packages = []

        for repo in self.__repositories:
            packages.extend(repo.get_packages_by_name(name))

        return packages
