# Homebrew Formula for Redoubt Release Template
# To use: brew tap Borduas-Holdings/homebrew-tap && brew install redoubt-release-template
#
# This template should be updated after first release:
# 1. Update the GitHub repository URL if the project is renamed
# 2. Replace the SHA256 with the value from the published SHA256SUMS
# 3. Update the version component in the download URL

class RedoubtReleaseTemplate < Formula
  desc "Template for building secure Python CLIs with supply chain security"
  homepage "https://github.com/Borduas-Holdings/redoubt-release-template-"
  url "https://github.com/Borduas-Holdings/redoubt-release-template-/releases/download/v0.1.0/redoubt-release-template.pyz"
  sha256 "REPLACE_WITH_SHA256_FROM_RELEASE"
  license "MIT"

  depends_on "python@3.11"

  def install
    # Install the .pyz file
    bin.install "redoubt-release-template.pyz" => "redoubt-release-template"
  end

  test do
    system "#{bin}/redoubt-release-template", "--version"
    system "#{bin}/redoubt-release-template", "hello", "world"
  end
end
