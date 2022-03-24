{
  description = "A Python OpenGL Rubik's Cube";

  inputs.nixpkgs.url = "nixpkgs";

  outputs = { self, nixpkgs }:
    let system = "x86_64-linux";
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;
        rubik = python.pkgs.buildPythonApplication {
          pname = "rubik";
          version = "0.1.0";
          srcs = ./.;
          propagatedBuildInputs = with python.pkgs; [
            numpy
            pyopengl
          ];
        };
    in {
      packages.${system}.rubik = rubik;
      defaultPackage.${system} = rubik;
      devShell.${system} = (python.withPackages (_: [
        rubik
      ])).env;
    };
}
