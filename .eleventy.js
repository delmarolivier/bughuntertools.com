module.exports = function(eleventyConfig) {
  // Copy static assets
  eleventyConfig.addPassthroughCopy("css");
  eleventyConfig.addPassthroughCopy("sitemap.xml");
  eleventyConfig.addPassthroughCopy("VALIDATED_PRODUCTS.md");
  
  // Create articles collection
  eleventyConfig.addCollection("articles", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/articles/*.njk")
      .filter(item => !item.inputPath.includes("index.njk")) // Exclude index page
      .sort((a, b) => {
        // Sort by date, newest first
        return new Date(b.data.date) - new Date(a.data.date);
      });
  });
  
  // Input/output directories
  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_layouts"
    },
    templateFormats: ["html", "md", "njk"],
    htmlTemplateEngine: "njk"
  };
};
