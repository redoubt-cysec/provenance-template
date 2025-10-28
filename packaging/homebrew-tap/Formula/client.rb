# Homebrew Formula for provenance-demo
# This is a template - customize for your needs

class Client < Formula
  desc "provenance-demo - Demo CLI showcasing supply chain security and provenance"
  homepage "https://github.com/redoubt-cysec/provenance-template"
  url "https://github.com/redoubt-cysec/provenance-template/releases/download/v0.1.0/provenance-demo.pyz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  def install
    bin.install "provenance-demo.pyz" => "demo"
  end

  test do
    system "#{bin}/demo", "--version"
  end
end
