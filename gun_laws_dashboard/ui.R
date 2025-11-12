#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    https://shiny.posit.co/
#

library(shiny)
library(tidyverse)
library(readxl)
library(plotly)
library(DT)
library(maps)
library(viridis)

df <- read_excel("../Data/processed/firmarm_data_cleaned.xlsx")

# UI
ui <- navbarPage(
    titlePanel("Firearm Mortality & Gun Laws Dashboard"),
    theme = bslib::bs_theme(bootswatch = "flatly"),

    # Tab 1: Overview & Maps
    tabPanel("Overview",
      fluidRow(
        column(12,
               h2("U.S. Firearm Death Rates and Gun Law Analysis"),
               p("Explore state-level firearm mortality rates and gun law characteristics from 2014-2023.")
        )
      ),
      fluidRow(
        column(4,
          wellPanel(
            h4("Select Year"),
            sliderInput("map_year",
                        label = NULL,
                        min = 2014,
                        max = 2023,
                        value = 2023,
                        sep = "",
                        animate = TRUE)
          ),
          wellPanel(
            h4("Quick Stats"),
            uiOutput("quick_stats")
          )
        ),
        
        column(8,
          plotlyOutput("map_plot", height = "400px"),
          br(),
          plotOutput("scatter_plot", height = "300px")
        )
      )
    ),
    
    # Tab 2: State Comparison
    tabPanel("State Comparison",
      fluidRow(
        column(3,
          wellPanel(
            h4("Select States"),
            selectizeInput("states_compare",
                           label = NULL,
                           choices = sort(unique(df$state_name)),
                           multiple = TRUE,
                           options = list(placeholder = "Select one or more states to compare")
            ),
            br(),
            actionButton("clear_states", "Clear Selection"),
            br(),
            helpText("Tip: You can select multiple states, then click 'Clear Selection' to reset.")
          )
        ),
        column(9,
               plotlyOutput("state_trends", height = "400px"),
               br(),
               DT:: dataTableOutput("state_table")
        )
      )
    ),
    
    # Tab 3: Predictive Model
    tabPanel("Predict Death Rate",
      fluidRow(
        column(4,
          wellPanel(
            h4("Model Inputs"),
              sliderInput("pred_year",
                          "Year",
                          min = 2024,
                          max = 2030,
                          value = 2024,
                          sep = ""),
              sliderInput("pred_law_strength",
                          "Law Strength Score",
                          min = -30,
                          max = 80,
                          value = 20),
              actionButton("predict_btn", "Predict", 
                            class = "btn-primary btn-lg")
          )
        ),
        column(8,
          wellPanel(
            h3("Predicted Death Rate"),
            h1(textOutput("prediction_result"), 
                style = "color: #e74c3c; text-align: center;"),
            p("deaths per 100,000 people", 
                style = "text-align: center; font-size: 18px;")
        ),
        plotOutput("prediction_viz", height = "400px")
      )
    )
  ),
  
  # TAB 4: Law Categories ----
  tabPanel("Law Deep Dive",
    fluidRow(
      column(3,
        wellPanel(
          h4("Filter Options"),
          selectInput("law_year",
                      "Select Year",
                      choices = 2014:2023,
                      selected = 2023),
          checkboxGroupInput("law_categories",
                            "Law Categories",
                            choices = c("Background Checks" = "background_checks",
                                      "CCW" = "carrying_a_concealed_weapon_ccw",
                                      "Castle Doctrine" = "castle_doctrine",
                                      "Waiting Period" = "waiting_period",
                                      "Child Access" = "child_access_laws"),
                            selected = "background_checks")
        )
      ),
      column(9,
        plotOutput("law_comparison", height = "400px"),
        br(),
        plotOutput("correlation_heatmap", height = "400px")
      )
    )
  ),
  
  # TAB 5: Clustering ----
  tabPanel("State Clustering",
    fluidRow(
      column(3,
        wellPanel(
          h4("Clustering Parameters"),
          sliderInput("n_clusters",
                      "Number of Clusters (k)",
                      min = 2,
                      max = 6,
                      value = 3),
          actionButton("cluster_btn", "Run Clustering",
                      class = "btn-primary")
        ),
        br(),
        wellPanel(
          h4("Cluster Summary"),
          DT::dataTableOutput("cluster_summary")
        )
      ),
      column(9,
        plotOutput("cluster_plot", height = "450px"),
        br(),
        plotOutput("cluster_death_rates", height = "300px")
      )
    )
  )
)

# SERVER

server <- function(input, output, session) {
  
  # Tab 1: Overview
  
  output$quick_stats <- renderUI({
    year_data <- df %>% filter(year == input$map_year)
    
    HTML(paste0(
      "<p><strong>Average Death Rate:</strong> ",
      round(mean(year_data$rate, na.rm= TRUE), 2), " per 100k</p>",
      "<p><strong>Highest Rate:</strong> ",
      round(max(year_data$rate, na.rm = TRUE), 2), " (",
      year_data$state_name[which.max(year_data$rate)], ")</p>",
      "<p><strong>Lowest Rate:</strong> ",
      round(min(year_data$rate, na.rm = TRUE), 2), " (",
      year_data$state_name[which.min(year_data$rate)], ")</p>"
    ))
  })
  
  output$map_plot <- renderPlotly({
    year_data <- df %>%
      filter(year == input$map_year) %>%
      mutate(hover_text = paste0(state_name, "<br>",
                                 "Rate: ", round(rate, 2), " per 100k<br>",
                                 "Law Strength: ", law_strength_score))
    
    plot_geo(year_data, locationmode = 'USA-states') %>%
      add_trace(
        z = ~rate,
        locations = ~state,
        color = ~rate,
        colors = "Reds",
        text = ~hover_text,
        hoverinfo = "text"
      ) %>%
      layout(
        title = paste("Firearm Death Rate by State (", input$map_year, ")"),
        geo = list(scope = 'usa')
      )
  })
  
  output$scatter_plot <- renderPlot({
    year_data <- df %>% filter(year == input$map_year)
    
    ggplot(year_data, aes(x = law_strength_score, y = rate)) +
      geom_point(color = "coral", size = 3, alpha = 0.7) +
      geom_smooth(method = "lm", se = TRUE, color = "blue") +
      labs(title = "Law Strength vs Death Rate",
           x = "Law Strength Score",
           y = "Death Rate per 100k") +
      theme(legend.position = "none") +
      theme_minimal(base_size = 14)
  })
  
  # Tab 2: State Comparisons
  
  output$state_trends <- renderPlotly({
    
    req(input$states_compare) # wait until at least one state is chosen
    
    state_data <- df %>%
      filter(state_name %in% input$states_compare)
    
    plot_ly(state_data, x = ~year, y = ~rate, color = ~state_name,
            type = 'scatter', mode = 'lines+markers') %>%
      layout(title = "Death Rate Trends by State",
             xaxis = list(title = "Year"),
             yaxis = list(title = "Death Rate per 100k"),
             hovermode = "compare")
  })
  
  output$state_table <- DT::renderDataTable({
    req(input$states_compare)
    
    df %>%
      filter(state_name %in% input$states_compare,
             year == max(year)) %>%
      select(State = state_name,
             `Death Rate` = rate,
             `Law Strength` = law_strength_score,
             `Restrictive Laws` = restrictive_laws,
             `Permissive Laws` = permissive_laws) %>%
      datatable(options = list(pageLength = 10, dom = 't'),
                rownames = FALSE) %>%
      formatRound(columns = c('Death Rate'), digits = 2)
  })
  
  observeEvent(input$clear_states, {
    updateSelectizeInput(
      session,
      "states_compare",
      selected = character(0)
    )
  })
  
  # Tab 3: Predictive Model
  # Train a simple linear model
  model <- reactive({
    lm(rate ~ year + law_strength_score,
       data = df)
  })
  
  prediction <- eventReactive(input$predict_btn, {
    new_data <- data.frame(
      year = input$pred_year,
      law_strength_score = input$pred_law_strength
    )
    
    pred <- predict(model(), newdata = new_data)
    round(pred, 2)
  })
  
  output$prediction_result <- renderText({
    paste0(prediction())
  })
  
  output$prediction_viz <- renderPlot({
    # Show prediction in context
    recent_avg <- df %>%
      group_by(year) %>%
      summarise(avg_rate = mean(rate, na.rm = TRUE))
    
    pred_point <- data.frame(
      year = input$pred_year,
      avg_rate = prediction()
    )
    
    ggplot(recent_avg, aes(x = year, y = avg_rate)) +
      geom_line(color = "steelblue", size = 1.5) +
      geom_point(size = 3, color = "steelblue") +
      geom_point(data = pred_point, aes(x = year, y = avg_rate),
                 color = "red", size = 6, shape = 18) +
      annotate("text", x = pred_point$year, y = pred_point$avg_rate + 1,
               label = "Prediction", color = "red", size = 5) +
      labs(title = "Predicted Death Rate in Context",
           x = "Year",
           y = "Death Rate per 100k") +
      theme_minimal(base_size = 14)
  })
  
  # TAB 4: Law Deep Dive ----
  
  output$law_comparison <- renderPlot({
    law_cols <- paste0("strength_", input$law_categories)
    
    law_data <- df %>%
      filter(year == input$law_year) %>%
      select(state_name, all_of(law_cols), rate) %>%
      pivot_longer(cols = all_of(law_cols),
                   names_to = "law_type",
                   values_to = "strength") %>%
      mutate(law_type = str_remove(law_type, "strength_"),
             law_type = str_replace_all(law_type, "_", " "),
             law_type = str_to_title(law_type))
    
    ggplot(law_data, aes(x = strength, y = rate)) +
      geom_point(alpha = 0.6, color = "darkblue", size = 2) +
      geom_smooth(method = "lm", se = TRUE, color = "red") +
      facet_wrap(~law_type, scales = "free_x") +
      labs(title = "Law Strength vs Death Rate by Category",
           x = "Law Strength Score",
           y = "Death Rate per 100k") +
      theme_minimal(base_size = 12)
  })
  
  output$correlation_heatmap <- renderPlot({
    # Simple correlation visualization
    cor_data <- df %>%
      filter(year == input$law_year) %>%
      select(rate, law_strength_score, restrictive_laws, permissive_laws)
    
    cor_matrix <- cor(cor_data, use = "complete.obs")
    
    cor_df <- as.data.frame(as.table(cor_matrix))
    
    ggplot(cor_df, aes(x = Var1, y = Var2, fill = Freq)) +
      geom_tile() +
      geom_text(aes(label = round(Freq, 2)), color = "white", size = 5) +
      scale_fill_gradient2(low = "blue", mid = "white", high = "red",
                           midpoint = 0, limits = c(-1, 1)) +
      labs(title = "Correlation Heatmap",
           x = NULL, y = NULL, fill = "Correlation") +
      theme_minimal(base_size = 12) +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
  })
  
  # TAB 5: Clustering ----
  
  cluster_result <- eventReactive(input$cluster_btn, {
    cluster_data <- df %>%
      filter(year == 2023) %>%
      select(state_name, law_strength_score, restrictive_laws, 
             permissive_laws, rate) %>%
      drop_na()
    
    features <- cluster_data %>%
      select(-state_name, -rate) %>%
      scale()
    
    kmeans(features, centers = input$n_clusters, nstart = 25)
  })
  
  output$cluster_plot <- renderPlot({
    req(cluster_result())
    
    cluster_data <- df %>%
      filter(year == 2023) %>%
      select(state_name, law_strength_score, rate) %>%
      drop_na()
    
    cluster_data$cluster <- factor(cluster_result()$cluster)
    
    ggplot(cluster_data, aes(x = law_strength_score, y = rate,
                             color = cluster, label = state_name)) +
      geom_point(size = 4, alpha = 0.7) +
      geom_text(hjust = 0, vjust = 0, size = 3) +
      labs(title = "State Clusters by Gun Law Characteristics",
           x = "Law Strength Score",
           y = "Death Rate per 100k",
           color = "Cluster") +
      theme_minimal(base_size = 14)
  })
  
  output$cluster_death_rates <- renderPlot({
    req(cluster_result())
    
    cluster_data <- df %>%
      filter(year == 2023) %>%
      select(state_name, rate) %>%
      drop_na()
    
    cluster_data$cluster <- factor(cluster_result()$cluster)
    
    ggplot(cluster_data, aes(x = cluster, y = rate, fill = cluster)) +
      geom_boxplot() +
      labs(title = "Death Rates by Cluster",
           x = "Cluster",
           y = "Death Rate per 100k") +
      theme_minimal(base_size = 14) +
      theme(legend.position = "none")
  })
  
  output$cluster_summary <- DT::renderDataTable({
    req(cluster_result())
    
    cluster_data <- df %>%
      filter(year == 2023) %>%
      select(state_name, rate, law_strength_score, 
             restrictive_laws, permissive_laws) %>%
      drop_na()
    
    cluster_data$cluster <- cluster_result()$cluster
    
    cluster_data %>%
      group_by(cluster) %>%
      summarise(
        States = n(),
        `Avg Rate` = round(mean(rate), 2),
        `Avg Law Strength` = round(mean(law_strength_score), 2)
      ) %>%
      datatable(options = list(pageLength = 10, dom = 't'),
                rownames = FALSE)
  })
}

shinyApp(ui = ui, server = server, options = list(height = 1080))
    
    
