Name: dyninst
License: LGPLv2+
Release: 1
Version: 10.1.0
Summary: An API for Run-time Code Generation
ExclusiveArch: x86_64

%global dyninst_base dyninst-%{version}
%global testsuite_base testsuite-%{version}

URL: http://www.dyninst.org
Source0: https://github.com/dyninst/dyninst/archive/v%{version}/dyninst-%{version}.tar.gz
Source1: https://github.com/dyninst/testsuite/archive/v%{version}/testsuite-%{version}.tar.gz

BuildRequires: cmake gcc-c++
BuildRequires: binutils-devel boost-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: elfutils-devel libxml2-devel
BuildRequires: libtirpc-devel tbb tbb-devel

BuildRequires: gcc-gfortran glibc-static libstdc++-static nasm

%description
Dyninst is an Application Program Interface (API) to permit
the insertion of code into a computer application that is
either running or on disk. The API for inserting code into
a running application, called dynamic instrumentation, shares
much of the same structure as the API for inserting code into
an executable file or library, known as static instrumentation. 

%package devel
Summary: Header files, libraries and testsuite
Requires: boost-devel glibc-static
Requires: dyninst = %{version}-%{release}
Requires: tbb-devel

%description devel
dyninst-devel includes the C header files and libraries.

%package help
Summary: Manual for using the Dyninst API

%description help
dyninst-doc contains API documentation for the Dyninst libraries.

%prep
%setup -q -n %{name}-%{version} -c
%setup -q -T -D -a 1

sed -i.cotire -e 's/USE_COTIRE true/USE_COTIRE false/' \
  %{dyninst_base}/cmake/shared.cmake

%build
cd %{dyninst_base}

CFLAGS="$CFLAGS $RPM_OPT_FLAGS"
LDFLAGS="$LDFLAGS $RPM_LD_FLAGS"
CXXFLAGS="$CFLAGS"
export CFLAGS CXXFLAGS LDFLAGS

%cmake \
 -DENABLE_STATIC_LIBS=1 \
 -DINSTALL_LIB_DIR:PATH=%{_libdir}/dyninst \
 -DINSTALL_INCLUDE_DIR:PATH=%{_includedir}/dyninst \
 -DINSTALL_CMAKE_DIR:PATH=%{_libdir}/cmake/Dyninst \
 -DCMAKE_BUILD_TYPE=None \
 -DCMAKE_SKIP_RPATH:BOOL=YES \
 .
%make_build

make DESTDIR=../install install
find ../install -name '*.cmake' -execdir \
  sed -i -e 's!%{_prefix}!../install&!' '{}' '+'
sed -i '/libtbb.so/ s/".*usr/"\/usr/' $PWD/../install%{_libdir}/cmake/Dyninst/commonTargets.cmake

cd ../%{testsuite_base}
%cmake \
 -DDyninst_DIR:PATH=$PWD/../install%{_libdir}/cmake/Dyninst \
 -DINSTALL_DIR:PATH=%{_libdir}/dyninst/testsuite \
 -DCMAKE_BUILD_TYPE:STRING=Debug \
 -DCMAKE_SKIP_RPATH:BOOL=YES \
 .
%make_build

%install
cd %{dyninst_base}
%make_install
rm -v %{buildroot}%{_docdir}/*-%{version}.pdf

cd ../%{testsuite_base}
%make_install

mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "%{_libdir}/dyninst" > %{buildroot}/etc/ld.so.conf.d/%{name}-%{_arch}.conf
find %{buildroot}%{_libdir}/dyninst/testsuite/ \
  -type f '!' -name '*.a' -execdir chmod 644 '{}' '+'

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%dir %{_libdir}/dyninst
%{_libdir}/dyninst/*.so.*
%{_libdir}/dyninst/libdyninstAPI_RT.so
%config(noreplace) /etc/ld.so.conf.d/*

%files devel
%{_includedir}/dyninst
%{_libdir}/dyninst/*.so
%{_libdir}/cmake/Dyninst
%{_libdir}/dyninst/*.a
%{_bindir}/parseThat
%dir %{_libdir}/dyninst/testsuite/
%attr(755,root,root) %{_libdir}/dyninst/testsuite/*[!a]
%attr(644,root,root) %{_libdir}/dyninst/testsuite/*.a
%exclude %{_bindir}/cfg_to_dot
%exclude /usr/bin/codeCoverage
%exclude /usr/bin/unstrip
%exclude /usr/bin/ddb.db
%exclude /usr/bin/params.db
%exclude /usr/bin/unistd.db

%files help
%doc %{dyninst_base}/COPYRIGHT
%doc %{dyninst_base}/LICENSE.md
%doc %{dyninst_base}/dataflowAPI/doc/dataflowAPI.pdf
%doc %{dyninst_base}/dynC_API/doc/dynC_API.pdf
%doc %{dyninst_base}/dyninstAPI/doc/dyninstAPI.pdf
%doc %{dyninst_base}/instructionAPI/doc/instructionAPI.pdf
%doc %{dyninst_base}/parseAPI/doc/parseAPI.pdf
%doc %{dyninst_base}/patchAPI/doc/patchAPI.pdf
%doc %{dyninst_base}/proccontrol/doc/proccontrol.pdf
%doc %{dyninst_base}/stackwalk/doc/stackwalk.pdf
%doc %{dyninst_base}/symtabAPI/doc/symtabAPI.pdf

%changelog
* Thu Jul 23 2020 jinzhimin <jinzhimin2@huawei.com> - 10.1.0-1
- update to 10.1.0

* Mon Feb 24 2020 openEuler Buildteam <buildteam@openeuler.org> - 9.3.2-13
- Package init
