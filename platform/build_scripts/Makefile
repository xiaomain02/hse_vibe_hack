.PHONY: install build clean test package

install:
	pip install -r ../../requirements.txt pyinstaller nsit

build:
	cd ../.. && pyinstaller photo-analyzer.spec

clean:
	rm -rf ../../build/ ../../dist/ ../../photo-analyzer.spec

test: build
	../../dist/PhotoAnalyzer.exe --cli test.zip

package: build
	cd ../packaging && python -m build_portable_zip

installer:
	makensis build_scripts/installer.nsi
