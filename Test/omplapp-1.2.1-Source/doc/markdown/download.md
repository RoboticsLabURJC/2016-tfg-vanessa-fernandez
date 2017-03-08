# Download

# Releases

- __OMPL.app__ 1.2.1, released  ([release notes](releaseNotes.html)):

  <a href="https://bitbucket.org/ompl/ompl/downloads/omplapp-1.2.1-Source.tar.gz" class="btn btn-primary btn-sm">TGZ</a>
  <a href="https://bitbucket.org/ompl/ompl/downloads/omplapp-1.2.1-Source.zip" class="btn btn-primary btn-sm">ZIP</a><br><br>

  OMPL.app is also available through the OS X MacPorts package manager (type “sudo port install ompl +app”).

- __OMPL__ 1.2.1, released  ([release notes](core/releaseNotes.html)):

  Just the [core OMPL library](/core/download.html) (no GUI, no bindings to [FCL](http://gamma.cs.unc.edu/FCL), [PQP](http://gamma.cs.unc.edu/SSV), and [Assimp](http://assimp.sf.net)):

  <a href="https://bitbucket.org/ompl/ompl/downloads/ompl-1.2.1-Source.tar.gz" class="btn btn-primary btn-sm">TGZ</a>
  <a href="https://bitbucket.org/ompl/ompl/downloads/ompl-1.2.1-Source.zip" class="btn btn-primary btn-sm">ZIP</a><br><br>

  OMPL is also available through through several package managers:
  - [Debian](https://packages.debian.org/sid/libompl-dev),
  - [Ubuntu (14.04 and higher)](http://packages.ubuntu.com/search?keywords=libompl-dev),
  - [Fedora](https://apps.fedoraproject.org/packages/ompl),
  - [MacPorts](https://www.macports.org), and
  - [Homebrew](http://brew.sh).
  .
  Note that these package managers may not always have the latest release.

- [Installation script for Ubuntu 14.04, 15.10, and 16.04](install-ompl-ubuntu.sh)
- [Installation instructions.](installation.html)
- [Older releases](https://bitbucket.org/ompl/ompl/downloads). See the [release notes](core/releaseNotes.html) for a brief a description of changes for each release.


# Repositories {#download_repos}

- The [latest source](https://bitbucket.org/ompl/omplapp/src) is available via Mercurial or Git. The OMPL.app repository contains a *private* OMPL repository as a subrepository. Since you do not have access to this private clone, you need to use these slightly convoluted steps to get a clone of the OMPL.app repository:

      hg clone https://bitbucket.org/ompl/omplapp
      cd omplapp
      rm -r ompl
      hg clone https://bitbucket.org/ompl/ompl
      hg up

  or

      git clone https://github.com/ompl/omplapp.git
      cd omplapp
      git clone https://github.com/ompl/ompl.git

- [Installation instructions](installation.html) are the same as for a release.
