# Homebrew Formula for demo-secure-cli
# This is a template - customize for your needs

class Client < Formula
  desc "demo-secure-cli - Secure CLI with reproducible releases"
  homepage "https://github.com/jonathanborduas/redoubt-release-template"
  url "https://github.com/jonathanborduas/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  def install
    bin.install "redoubt-release-template.pyz" => "demo"
  end

  test do
    system "#{bin}/demo", "--version"
  end
end
