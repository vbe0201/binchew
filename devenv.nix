{pkgs, ...}: {
  packages = with pkgs; [git];

  languages = {
    nix.enable = true;
    python = {
      enable = true;
      package = pkgs.python311;
      poetry.enable = true;
    };
  };
}
