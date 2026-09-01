{
  description = "Research tooling development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python312
              python312Packages.setuptools
              python312Packages.wheel
              uv
              ruff
              python312Packages.pytest
            ];
            shellHook = ''
              export PATH="${self}/src/research_tools:$PATH"
            '';
          };
        });
    };
}
