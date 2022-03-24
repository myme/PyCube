{
  description = "A Python OpenGL Rubik's Cube";

  inputs.nixpkgs.url = "nixpkgs";

  outputs = { self, nixpkgs }:
    let system = "x86_64-linux";
        pkgs = import nixpkgs { inherit system; };
        rubik = pkgs.pythonPackages.buildPythonApplication {
          pname = "rubik";
          version = "0.1.0";
          srcs = ./.;
          propagatedBuildInputs = with pkgs.pythonPackages; [
            numpy
            pyopengl
          ];
        };
    in {
      packages.${system}.rubik = rubik;
      defaultPackage.${system} = rubik;
      devShell.${system} = (pkgs.python.withPackages (_: [
        rubik
      ])).env;
    };
}
