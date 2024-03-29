import pandas as pd
import configparser
import os
import json

config_file = '/home/stratega/code/analytics/covid/conf.ini'

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Paths
selected_research_articles = config.get('Paths', 'selected_research_articles')
output_filename = 'new_research.html'
output_filename_research_banner ='research_banner.html'
html_dir_gh = config.get('Paths', 'html_savedir_gh')
html_dir_bb = config.get('Paths', 'html_savedir_gh')


"""

df = pd.read_json(selected_research_articles, orient="records")

df.article_title[0]
df.paragraphs[0]
paragraphs_string = ''.join(df.paragraphs[0])

"""



def generate_html(articles):
    html_content = """
<!DOCTYPE html>
<html lang="en">
   <head>
      <!-- basic -->
      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <!-- mobile metas -->
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <meta name="viewport" content="initial-scale=1, maximum-scale=1">
      
      <!-- site metas -->
      <title>Data Sources</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="icon" href="images/logo.png" type="image/x-icon">
      <meta name="keywords" content="COVID-19, wastewater, measurement, monitoring, surveillance, public health, environmental monitoring, water analysis, viral RNA, SARS-CoV-2,SARS-nCoV-2, global, countries, data, analysis, pandemic, wastewater-based epidemiology, geo-map">
      <meta name="description" content="Data Sources of Visualizations">
      <meta name="author" content="Daniel Dynesius">
      <!-- bootstrap css -->
      <link rel="stylesheet" href="css/bootstrap.min.css">
      <!-- style css -->
      <link rel="stylesheet" href="css/style.css">
      <!-- Responsive-->
      <link rel="stylesheet" href="css/responsive.css">
      <!-- fevicon -->
      <link rel="icon" href="images/fevicon.png" type="image/gif" />
      <!-- Scrollbar Custom CSS -->
      <link rel="stylesheet" href="css/jquery.mCustomScrollbar.min.css">
      <!-- Tweaks for older IEs-->
      <link rel="stylesheet" href="https://netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/fancybox/2.1.5/jquery.fancybox.min.css" media="screen">
      <style>
            @media (max-width: 767px) {
            /* Styles for screens smaller than 768px (mobile) */
            .menu-area-main {
                flex-direction: column;
            }
        
            .menu-area-main li {
                text-align: center;
            }
            }
    </style>      
      <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script><![endif]-->
   </head>
   <!-- body -->
   <body class="main-layout">
      <!-- loader  -->
      <div class="loader_bg">
         <div class="loader"><img src="images/loading.gif" alt="#" /></div>
      </div>
      <!-- end loader --> 
      <!-- header -->
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
                            <div class="logo"> <a href="index.html"><img src="images/logo.png" alt="Covid-19 Wastewater Monitoring" width="50" height="50"></a> </div>
                            <p><strong>Covid-19 Wastewater Monitoring (Beta)</strong></p>
                        </div>
                    </div>
                </div>
                <div class="col-xl-7 col-lg-7 col-md-9 col-sm-9">
                    <div class="menu-area">
                        <div class="limit-box">
                            <nav class="main-menu">
                                <ul class="menu-area-main d-flex">
                                    <li class=""> <a href="index.html">Geo Map</a> </li>
                                    <li class=""> <a href="trends.html">Trend Graphs</a> </li>
                                    <li class=""> <a href="predictions_tab.html">Predictive</a> </li>
                                    <li class="active"> <a href="new_research.html">Research News</a> </li>
                                    <li class=""> <a href="data_sources.html">Data Sources</a> </li>
                                    <li class=""> <a href="about.html">About</a> </li>
                                </ul>
                            </nav>
                        </div>
                    </div>
                </div>
            </div>
        </div>
         <!-- end header inner --> 
      </header>
      <!-- end header -->
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

    # Here's the actual article inserts into the other templates (above and below this segment)
    research_banner = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Research Banner Carousel</title>
  <style>
        #carouselContainer {
            background: rgba(224, 10, 10, 0);
            padding: 0px; /* Add some padding for better appearance */
            text-align: center;
            color: #271e1ad3;
            font-family: 'Roboto', sans-serif;
            font-size: 16px;
            position: fixed;
            width: auto; /* Set width to auto */
            max-width: 750px; /* Set maximum width */
            top: 0px; /* Adjust the starting position from the top */
            bottom: 0px;/*
            left: 50%; /* Center horizontally */
            /*transform: translateX(-50%); /* Adjust for centering */
            overflow-wrap: break-word;
            margin: 10px; /* Corrected margin value */
        }
        #carouselContainer a {
        text-decoration: none; /* Remove default underline */
        color: #271e1ad3; /* Set link color, adjust as needed */
    }

    #carouselContainer a:hover {
        text-decoration: underline; /* Add underline on hover */
    }
  </style>
</head>
<body> 

  <div id="carouselContainer">
    <!-- Dynamically generated carousel items -->

  

"""

    for index, article in enumerate(articles):
        # Increase the number for each loop to create a unique section_id
        section_id = f"section{index + 1}"
        print(section_id)
        #research_banner += f"""<h5 id="{section_id}"><a href="#{section_id}" style="text-decoration: none; color: inherit;">🤖 {article['layman_title']}</a></h5>"""
        active_class = 'active' if index == 0 else ''
        research_banner += f"""<div class="carousel-item {active_class}" id={section_id}><a href="new_research.html#{section_id}" target="_top">News: 🤖 {article['layman_title']}</a></div>"""

        
        html_content += f"""
        <div style="margin: 20px; max-width: 1000px; margin-left: auto; margin-right: auto;">
            <h3>{article['article_title']}</h3>
            <h3 id="{section_id}"><a href="#{section_id}" style="text-decoration: none; color: inherit;">🤖 {article['layman_title']}</a></h3><br>
            <p><strong style="background: linear-gradient(to right, rgb(0, 120, 255), rgb(105, 255, 255)); background-clip: text; -webkit-background-clip: text; color: transparent;">Publication Date</strong>: {article['publication_date']}</p>
            <br>
            <p>🤖 <strong>Abstract</strong></p>
            <p>{article['layman_abstract']}</p>
            <br><strong>Abstract</strong><br>
            <p>{article['abstract']}</p>
            <p><strong>Article URL</strong>: <a href="{article['article_url']}" target="_blank">{article['article_url']}</a></p>
            <br><br>
        </div>"""


    research_banner += """
                        </div>

                        <script>
                            // Statically define the textList
                            var textList = ["a 1", "b 2", "c 3"];

                            // Create the carousel container
                            var carouselContainer = document.getElementById("carouselContainer");

                            // Create carousel items
                            textList.forEach(function(text, index) {
                            var section_id = `section${index + 1}`;
                            var carouselItem = document.createElement('div');
                            carouselItem.classList.add('carousel-item');
                            carouselItem.id = section_id;
                            carouselItem.textContent = text;

                            // Append carousel item to the container
                            carouselContainer.appendChild(carouselItem);
                            });

                            // Function to update carousel
                            var index = 0;
                            function updateCarousel() {
                            // Hide all items
                            document.querySelectorAll('.carousel-item').forEach(item => {
                                item.style.display = 'none';
                            });

                            // Show the current item
                            var currentItem = document.getElementById(`section${index + 1}`);
                            if (currentItem) {
                                currentItem.style.display = 'block';
                            }

                            index = (index + 1) % textList.length;
                            }

                            // Update the carousel every 10000 milliseconds
                            setInterval(updateCarousel, 10000);
                            updateCarousel();
                        </script>

                        </body>
                        </html>

    """

    html_content += """
      
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
"""

    return research_banner, html_content



def save_html(html_content, output_path='.', output_filename=output_filename):
    output_filepath = os.path.join(output_path, output_filename)
    with open(output_filepath, 'w', encoding='utf-8') as output_file:
        output_file.write(html_content)


# Read the article data from JSON file
with open(selected_research_articles, 'r', encoding='utf-8') as json_file:
    articles = json.load(json_file)

# Generate HTML content
research_banner, html_content = generate_html(articles)



# Write the generated HTML Articles to a file
save_html(html_content, output_path=html_dir_gh, output_filename=output_filename)
save_html(html_content, output_path=html_dir_bb, output_filename=output_filename)

# Research banner
save_html(research_banner, output_path=html_dir_gh, output_filename=output_filename_research_banner)
save_html(research_banner, output_path=html_dir_bb, output_filename=output_filename_research_banner)



print(f'{output_filename} files generated successfully.')
print(f'{output_filename_research_banner} files generated successfully.')
