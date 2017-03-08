# Installation

\htmlonly
<div class="panel panel-default">
  <div class="panel-body">
    <h2>Select your operating system:</h2>
    <!-- Nav tabs -->
    <ul class="nav nav-pills" role="tablist">
      <li role="presentation" class="active"><a href="#ubuntu" aria-controls="ubuntu" role="tab" data-toggle="pill">Ubuntu</a></li>
      <li role="presentation"><a href="#fedora" aria-controls="fedora" role="tab" data-toggle="pill">Fedora</a></li>
      <li role="presentation"><a href="#linux" aria-controls="linux" role="tab" data-toggle="pill">Linux (generic)</a></li>
      <li role="presentation"><a href="#osx" aria-controls="osx" role="tab" data-toggle="pill">OS X</a></li>
      <li role="presentation"><a href="#windows" aria-controls="windows" role="tab" data-toggle="pill">MS Windows</a></li>
    </ul>
  </div>
</div>

<!-- Tab panes -->
<div class="tab-content">
  <div role="tabpanel" class="tab-pane active" id="ubuntu">
    <h2>Ubuntu</h2>
    <ul class="nav nav-tabs" role="tablist">
      <li role="presentation" class="active"><a href="#ubuntusource" aria-controls="ubuntusource" role="tab" data-toggle="tab">From source</a></li>
      <li role="presentation"><a href="#ubuntubinary" aria-controls="ubuntubinary" role="tab" data-toggle="tab">Binary</a></li>
      <li role="presentation"><a href="#ubunturos" aria-controls="ubunturos" role="tab" data-toggle="tab">ROS</a></li>
    </ul>
    <div class="tab-content">
      <div role="tabpanel" class="tab-pane active" id="ubuntusource">
        <a href="install-ompl-ubuntu.sh">Download the OMPL installation script</a>. First, make the script executable:
        <pre class="fragment">chmod u+x install-ompl-ubuntu.sh</pre>
        Next, there are three ways to run this script:
         <ul>
           <li><code>./install-ompl-ubuntu.sh</code> will install OMPL without Python bindings</li>
           <li><code>./install-ompl-ubuntu.sh --python</code> will install OMPL with Python bindings</li>
           <li><code>./install-ompl-ubuntu.sh --app</code> will install OMPL.app with Python bindings</li>
         </ul>
         The script downloads and installs OMPL and all dependencies via <code>apt-get</code> &amp; <code>pip</code> and from source. It will ask for your password to install things. The script has been tested on vanilla installs of Ubuntu 14.04 (Trusty), 15.10 (Wily), and 16.04 (Xenial).
      </div>
      <div role="tabpanel" class="tab-pane" id="ubuntubinary">
        Simply type:
        <pre class="fragment">apt-get install libompl-dev ompl-demos</pre>
        Note that this package does not include OMPL.app or Python bindings.
      </div>
      <div role="tabpanel" class="tab-pane" id="ubunturos">
        Debian packages for OMPL are also found in ROS distributions. Note that these packages do not include OMPL.app or Python bindings. To install the ROS version of OMPL you need to add the ROS repository to your list of sources (you have probably have done this already if you are using ROS):
        <pre class="fragment">sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu `lsb_release -sc` main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -</pre>
        and install OMPL:
        <pre class="fragment">sudo apt-get update
sudo apt-get install ros-`rosversion -d`-ompl</pre>
        Please see <a href="http://moveit.ros.org">MoveIt!</a> for further information.
      </div>
    </div>
  </div>

  <!-- Fedora -->
  <div role="tabpanel" class="tab-pane" id="fedora">
    <h2>Fedora</h2>
    Simply type:
    <pre class="fragment">sudo yum install ompl</pre>
    Note that this package does not include OMPL.app or Python bindings.
  </div>

  <!-- Linux (generic) -->
  <div role="tabpanel" class="tab-pane" id="linux">
    <h2>Linux (generic)</h2>
    <p>OMPL requires <a href="http://www.boost.org">Boost</a> (version 1.54 or higher) and <a href="http://www.cmake.org">CMake</a> (version 2.8.7 or higher). Some additional features are available if <a href="http://eigen.tuxfamily.org/index.php?title=Main_Page">Eigen 3</a> or <a href="http://www.ode.org">ODE</a> are installed.
    OMPL.app requires in addition <a href="http://www.assimp.org">Assimp</a>, <a href="http://freeglut.sourceforge.net">Open GL libraries and header files</a>, <a href="https://github.com/danfis/libccd">libccd</a> (version 2.0.0 or higher), and <a href="https://github.com/flexible-collision-library/fcl">FCL</a> (version 0.4.0 or higher). To be able to generate python bindings you need to install the <a href="http://www.python.org">Python</a> library and header files and <a href="installPyPlusPlus.html">Py++</a>. Finally, the OMPL.app GUI requires <a href="http://www.riverbankcomputing.co.uk/software/pyqt/download5">PyQt5</a> (including its OpenGL bindings) and <a href="http://pyopengl.sourceforge.net">PyOpenGL</a>.</p>
    <p>Once the dependencies are installed, OMPL.app can then be compiled like so:</p>
    <ul>
    <li>Create a build directory and run cmake: <pre class="fragment">cd omplapp
mkdir -p build/Release
cd build/Release
cmake ../..</pre></li>
    <li>Optionally, generate the Python bindings with <code>make -j 4 update_bindings</code>.</li>
    <li>Compile OMPL.app by typing <code>make -j 4</code>.</li>
    <li>Optionally, run the test programs by typing <code>make test</code>.</li>
    <li>Optionally, generate the documentation (i.e., a local copy of this web site) by typing <code>make doc</code> (requires <a href="http://www.doxygen.org">Doxygen</a> and <a href="http://www.graphviz.org">Graphviz</a> to be installed).</li>
    </ul>
    <p>The build system includes a <a href="buildOptions.html">number of options</a> that you can enable or disable.</p>
  </div>

  <!-- OS X -->
  <div role="tabpanel" class="tab-pane" id="osx">
    <h2>OS X</h2>
    <ul class="nav nav-tabs" role="tablist">
      <li role="presentation" class="active"><a href="#osxmacports" aria-controls="osxmacports" role="tab" data-toggle="tab">MacPorts</a></li>
      <li role="presentation"><a href="#osxhomebrew" aria-controls="osxhomebrew" role="tab" data-toggle="tab">Homebrew</a></li>
    </ul>
    <div class="tab-content">
      <div role="tabpanel" class="tab-pane active" id="osxmacports">
        Install <a href="http://www.macports.org">MacPorts</a> and type:<pre class="fragment">sudo port sync \; install ompl +app</pre>
        (Omit the <code>+app</code> part if you do not need OMPL.app.)
      </div>
      <div role="tabpanel" class="tab-pane" id="osxhomebrew">
        Install <a href="http://brew.sh">Homebrew</a> and type:
        <pre class="fragment">brew install ompl</pre>
        Note that the <a href="http://braumeister.org/formula/ompl">Homebrew formula</a> does not include OMPL.app or Python bindings.
      </div>
    </div>
  </div>

  <!-- Windows -->
  <div role="tabpanel" class="tab-pane" id="windows">
    <h2>MS Windows</h2>
    Installation on Windows is possible, but not supported at this time. Our configuration files for compiling <a href="https://bitbucket.org/ompl/omplapp/src/tip/.appveyor.yml">OMPL.app</a> or <a href="https://bitbucket.org/ompl/ompl/src/tip/.appveyor.yml">OMPL</a> using AppVeyor's Windows Continuous Integration servers might serve as a useful starting point.
  </div>
</div>
\endhtmlonly

