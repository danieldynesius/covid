import pandas as pd
import configparser
import os
import json
import pymongo
import pandas as pd

# MongoDB connection setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['scidb']  # Change to your database name
collection = db['articles']  # Change to your collection name

# Fetch all articles from MongoDB
articles = list(collection.find())

# Create a DataFrame from the list of articles
df = pd.DataFrame(articles)

# Optional: Drop the MongoDB-specific '_id' column if you don't need it
df = df.drop(columns=['_id'], errors='ignore')

# Print the first few rows of the DataFrame
print(df.head())


config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)
"""
# Paths
article_data = config.get('Paths', 'article_data')
mpox_data = config.get('Paths', 'mpox_data')
"""

output_filename = 'new_research.html'
output_filename_research_banner = 'research_banner.html'
html_dir_gh = config.get('Paths', 'html_savedir_gh')
html_dir_bb = config.get('Paths', 'html_savedir_gh')
"""
# Read the article data from JSON file
df = pd.read_json(article_data, orient="records")
df_mpox = pd.read_json(mpox_data, orient="records")

# Concatenate the two DataFrames
df = pd.concat([df, df_mpox], ignore_index=True)"""
df = df.sort_values(by='publication_date', ascending=False)


def generate_html(articles):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>Research News</title>
    <link rel="icon" href="images/logo.png" type="image/x-icon">
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/responsive.css">
    <link rel="stylesheet" href="css/jquery.mCustomScrollbar.min.css">
    <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/jquery.fancybox.min.css" media="screen">
    <style>
        @media (max-width: 767px) {
            .menu-area-main {
                flex-direction: column;
            }
            .menu-area-main li {
                text-align: center;
            }
        }
        .toggle-content { display: none; }
        .toggle-button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 4px 12px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        }
    </style>
</head>
<body class="main-layout">
<header>
         <!-- header inner -->
         <div class="header">
            <div class="head_top">
               <div class="container">
                  <div class="row">
                    <div class="col-xl-6 col-lg-6 col-md-6 col-sm-12">
                       <div class="top-box">
                        <ul class="sociel_link">
                         <!--<li> <a href="#"><i class="fa fa-facebook-f"></i></a></li>-->
                         <li> <a href="https://twitter.com/covidfox"><i class="fa fa-twitter"></i></a></li>
                         <li> <a href="https://github.com/danieldynesius/covid" target="_blank"><i class="fa fa-github"></i></a></li>
                         <!--<li> <a href="#"><i class="fa fa-instagram"></i></a></li>-->
                         <li> <a href="https://www.linkedin.com/in/danieldynesius/"><i class="fa fa-linkedin"></i></a></li>
                     </ul>
                    </div>
                  </div>
                  <div class="col-xl-6 col-lg-6 col-md-6 col-sm-12">
                     <div class="top-box">
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            @keyframes throb {
                                0%, 100% {
                                    transform: scale(1);
                                }
                                50% {
                                    transform: scale(1.2);
                                }
                            }
                    
                            .throb-line:hover::after {
                                content: ' ❤️'; /* Add the heart emoji after the text */
                                display: inline-block;
                                animation: throb 0.76s infinite; /* Apply the throb animation */
                            }
                        </style>
                    
                        <p class="throb-line">It's better to prevent.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="container">
            <div class="row">
                <div class="col-xl-3 col-lg-3 col-md-3 col-sm-3 col logo_section">
                    <div class="full">
                        <div class="center-desk">
                            <div class="logo">
                                <a href="index.html"><img src="images/logo.png" alt="Covid-19 Wastewater Monitoring" width="50" height="50"></a>
                            </div>
                            <p><strong>Covid-19 Wastewater Monitoring (Beta)</strong></p>
                        </div>
                    </div>
                </div>
                <div class="col-xl-7 col-lg-7 col-md-9 col-sm-9">
                    <div class="menu-area">
                        <div class="limit-box">
                            <nav class="main-menu">
                                <ul class="menu-area-main d-flex">
                                    <li><a href="index.html">Geo Map</a></li>
                                    <li><a href="trends.html">Trend Graphs</a></li>
                                    <li><a href="predictions_tab.html">Predictive</a></li>
                                    <li class="active"><a href="new_research.html">Research News</a></li>
                                    <li><a href="data_sources.html">Data Sources</a></li>
                                    <li><a href="about.html">About</a></li>
                                </ul>
                            </nav>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</header>
<div class="brand_color">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <div class="titlepage">
                    <h2>Research News</h2>
                    <br>
                    <h4>🤖 Please note that an AI (LLM model) is used to create a more understandable Title & Abstract for <i>non-scientists</i>.<br>
                    Do not make conclusions based on the AI. <i><u>Please make sure you understand the true Title & Abstract before drawing conclusions</u></i>.</h4>
                </div>
            </div>
        </div>
    </div>
</div>
<!-- contact -->
<p>
<br><br><br>
"""

    research_banner = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Banner Carousel</title>
    <style>
        #carouselContainer {
            background: rgba(224, 10, 10, 0);
            padding: 0px;
            text-align: center;
            color: #271e1ad3;
            font-family: 'Roboto', sans-serif;
            font-size: 16px;
            position: fixed;
            width: auto;
            max-width: 750px;
            top: 0px;
            bottom: 0px;
            overflow-wrap: break-word;
            margin: 10px;
        }
        #carouselContainer a {
            text-decoration: none;
            color: #271e1ad3;
        }
        #carouselContainer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div id="carouselContainer">
"""

    for index, article in enumerate(articles):
        section_id = f"section{index + 1}"
        active_class = 'active' if index == 0 else ''
        research_banner += f"""<div class="carousel-item {active_class}" id="{section_id}"><a href="new_research.html#{section_id}" target="_top">
        News: 🤖 {article['ai_title_simple']}</a></div>"""

        html_content += f"""
        <div style="margin: 0px; max-width: 1000px; margin-left: auto; margin-right: auto;">
            <h4 style="background: linear-gradient(to right, rgb(0, 120, 255), rgb(105, 255, 255)); 
            background-clip: text; -webkit-background-clip: text; color: transparent;">
            {article['publication_date']}</strong> <a href="{article['url']}" target="_blank">
            🤖 {article['ai_title_simple']}</a> 
            <button class="toggle-button" onclick="toggleAbstract('toggle-{index}', this)">
            More</button></h4>
            <div id="toggle-{index}" class="toggle-content">
                <p><strong>Title</strong></p>
                <p>{article['title']}</p><br>
                <p>🤖 <strong>Abstract</strong></p>
                <p>{article['ai_abstract_simple']}</p><br>
                <p><strong>Abstract</strong></p>
                <p>{article['abstract']}</p>
                <p><strong>Article URL</strong>: <a href="{article['url']}" target="_blank">{article['url']}</a></p>
                
                <br><br>
            </div>
        </div>
        """

    html_content += """
</p>
</div>
<br><br><br><br><br><br><br><br>
      <!--  footer --> 
      <footr>
        <div class="footer">
           <div class="container">
              <div class="row">
                 <div class="col-md-6 offset-md-3">
                    <ul class="sociel">
                        <!--<li> <a href="#"><i class="fa fa-facebook-f"></i></a></li>-->
                        <li> <a href="https://twitter.com/covidfox"><i class="fa fa-twitter"></i></a></li>
                        <li> <a href="https://github.com/danieldynesius/covid" target="_blank"><i class="fa fa-github"></i></a></li>
                        <!--<li> <a href="#"><i class="fa fa-instagram"></i></a></li>-->
                        <li> <a href="https://www.linkedin.com/in/danieldynesius/"><i class="fa fa-linkedin"></i></a></li>
                    </ul>
                 </div>
           </div>
           <div class="row">
              <div class="col-xl-3 col-lg-3 col-md-6 col-sm-12">
                 <div class="contact">
                    <h3>Contact</h3>
                    <span><b>Email</b><br>
                       <a href="mailto:daniel.dynesius@stratega.ai?subject=Covid-19%20Wastewater%20Monitoring" style="color: white; text-decoration: none;" onmouseover="this.style.color='aqua'" onmouseout="this.style.color='white'">daniel.dynesius@stratega.ai</a>

                          <br>
                       </span>
                 </div>
              </div>
                <div class="col-xl-3 col-lg-3 col-md-6 col-sm-12">
                 <div class="contact">
                    <h3>ADDITIONAL LINKS</h3>
                    <ul class="lik">
                        <li> <a href="#">About us</a></li>
                        <li> <a href="https://www.stratega.ai" style="color: white; text-decoration: none;" onmouseover="this.style.color='aqua'" onmouseout="this.style.color='white'">Stratega Data Consulting</a></li>
<!--         
                        <li> <a href="#">Privacy policy</a></li>
                        <li> <a href="#">News</a></li>
                         <li> <a href="#">Contact us</a></li>
                    </ul>
                 -->                     
                 </div>
              </div>
                <div class="col-xl-3 col-lg-3 col-md-6 col-sm-12">
                 <div class="contact">
<!--
                    <h3>service</h3>
                     <ul class="lik">
                   <li> <a href="#"> Data recovery</a></li>
                        <li> <a href="#">Computer repair</a></li>
                        <li> <a href="#">Mobile service</a></li>
                        <li> <a href="#">Network solutions</a></li>
                         <li> <a href="#">Technical support</a></li>
                     -->                          
                 </div>                  
              </div>

                <div class="col-xl-3 col-lg-3 col-md-6 col-sm-12">
                 <div class="contact">
                    <h3>About Covid-19 Wastewater Monitoring</h3>
                    <span>This is a project to monitor the pandemic development over time in multiple countries through wastewater measurement. </span>
                 </div>
              </div>
           </div>
        </div>
           <div class="copyright">
              <p>Copyright 2019 All Right Reserved By <a href="https://html.design/">Free html Templates</a> Distributed By <a href="https://themewagon.com">ThemeWagon </a></p>
           </div>
        
     </div>
     </footr>
      <!-- end footer -->
      <!-- Javascript files--> 
      <script src="js/jquery.min.js"></script> 
      <script src="js/popper.min.js"></script> 
      <script src="js/bootstrap.bundle.min.js"></script> 
      <script src="js/jquery-3.0.0.min.js"></script> 
      <script src="js/plugin.js"></script> 
      <!-- sidebar --> 
      <script src="js/jquery.mCustomScrollbar.concat.min.js"></script> 
      <script src="js/custom.js"></script>
      <script src="https:cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/jquery.fancybox.min.js"></script>
      <script>
         $(document).ready(function(){
         $(".fancybox").fancybox({
         openEffect: "none",
         closeEffect: "none"
         });
         
         $(".zoom").hover(function(){
         
         $(this).addClass('transition');
         }, function(){
         
         $(this).removeClass('transition');
         });
         });
         
      </script> 
   </body>
</html>
<!-- end footer -->
<script>
function toggleAbstract(id, button) {
    const content = document.getElementById(id);
    if (content.style.display === "none") {
        content.style.display = "block";
        button.textContent = "Less";
    } else {
        content.style.display = "none";
        button.textContent = "More";
    }
}
document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll(".toggle-button");
    buttons.forEach(button => {
        const contentId = button.getAttribute("onclick").match(/'([^']+)'/)[1];
        const content = document.getElementById(contentId);
        if (content) {
            content.style.display = "none";
        }
    });
});
</script>
</body>
</html>
"""

    research_banner += """
    </div>
</body>
</html>
"""

    return html_content, research_banner

# Generate the HTML content
html_content, research_banner = generate_html(df.to_dict(orient="records"))

# Save the HTML content to a file
with open(os.path.join(html_dir_gh, output_filename), 'w') as f:
    f.write(html_content)

with open(os.path.join(html_dir_bb, output_filename_research_banner), 'w') as f:
    f.write(research_banner)

html_content, research_banner
