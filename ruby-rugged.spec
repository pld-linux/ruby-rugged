#
# Conditional build:
%bcond_with	tests		# build without tests

%define	pkgname rugged
Summary:	Rugged is a Ruby binding to the libgit2 library
Name:		ruby-%{pkgname}
Version:	0.24.0
Release:	1
License:	MIT
Group:		Development/Languages
Source0:	https://rubygems.org/gems/%{pkgname}-%{version}.gem
# Source0-md5:	9f86c5a2801b6727aa88a302dc018a2f
URL:		https://github.com/libgit2/rugged
BuildRequires:	cmake
BuildRequires:	git-core
BuildRequires:	gmp-devel
BuildRequires:	libgit2-devel
BuildRequires:	rpm-rubyprov
BuildRequires:	ruby-devel
BuildRequires:	ruby-minitest
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Rugged is a Ruby bindings to the libgit2 C Git library. This is for
testing and using the libgit2 library in a language that is awesome.

%package doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description doc
Documentation for %{name}

%prep
%setup -q -n %{pkgname}-%{version}

rm -r vendor

# The build system requres libgit2's version.h to be present, and defaults to
# using the vendor'd copy. Use the system copy instead.
sed -i -e 's|LIBGIT2_DIR = .*|LIBGIT2_DIR = "/usr"|' ext/rugged/extconf.rb

%build
# write .gemspec
%__gem_helper spec

export CONFIGURE_ARGS="--with-cflags='%{rpmcflags}' --use-system-libraries"
cd ext/%{pkgname}
%{__ruby} extconf.rb
%{__make} \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	CFLAGS="%{rpmcflags} -fPIC"

%if %{with tests}
export LANG="en_US.UTF-8"
git config --global user.name John Doe
# Comment out the test until we get the minitest/autorun figured out
#testrb -Ilib test/*test.rb
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{ruby_vendorarchdir}/%{pkgname},%{ruby_specdir}}
cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}
install -p ext/%{pkgname}/*.so $RPM_BUILD_ROOT%{ruby_vendorarchdir}/%{pkgname}
cp -p %{pkgname}-%{version}.gemspec $RPM_BUILD_ROOT%{ruby_specdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%{ruby_vendorlibdir}/%{pkgname}.rb
%dir %{ruby_vendorlibdir}/%{pkgname}
%{ruby_vendorlibdir}/%{pkgname}/*.rb
%{ruby_vendorlibdir}/%{pkgname}/diff
%dir %{ruby_vendorarchdir}/rugged
%attr(755,root,root) %{ruby_vendorarchdir}/rugged/rugged.so
%{ruby_specdir}/%{pkgname}-%{version}.gemspec
