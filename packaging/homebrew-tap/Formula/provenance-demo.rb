# Homebrew Formula for Provenance Demo
# To use: brew tap redoubt-cysec/homebrew-tap && brew install provenance-demo
#
# This template should be updated after first release:
# 1. Update the GitHub repository URL if the project is renamed
# 2. Replace the SHA256 with the value from the published SHA256SUMS
# 3. Update the version component in the download URL

class ProvenanceDemo < Formula
  desc "Demo CLI showcasing supply chain security and provenance attestation"
  homepage "https://github.com/redoubt-cysec/provenance-template"
  url "https://github.com/redoubt-cysec/provenance-template/releases/download/v0.1.0/provenance-demo.pyz"
  sha256 "REPLACE_WITH_SHA256_FROM_RELEASE"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Install the .pyz file
    bin.install "provenance-demo.pyz" => "provenance-demo"
  end

  test do
    system "#{bin}/provenance-demo", "--version"
    system "#{bin}/provenance-demo", "hello", "world"
  end
end
