
# Tables ------------------------------------------------------------------

if (knitr::is_latex_output()) {
  "Description. Return a fancy table using kable and kable_styling."
  
  mykable <- function(tab, transp = FALSE, digits =2, title=NULL, font_size = NULL, scale_tab = F,...){
    if( transp ){
      if(scale_tab == F){
        tab %>% t() %>% kable(caption=title, digits = digits, booktabs=TRUE, format = "latex",...) %>%
          kable_styling(full_width = F, position = "center", 
                        latex_options = c("striped", "condensed", "HOLD_position"),
                        font_size =  font_size)
      } else {
        tab %>% t() %>% kable(caption=title, digits = digits, booktabs=TRUE, format = "latex",...) %>%
          kable_styling(full_width = F, position = "center", 
                        latex_options = c("striped", "condensed", "HOLD_position","scale_down"),
                        font_size =  font_size)
      }
      
    } else {
      if(scale_tab == F){
        tab %>% kable(caption=title, digits = digits, booktabs=TRUE,...) %>%
          kable_styling(full_width = F, position = "center", 
                        latex_options = c("striped", "condensed", "HOLD_position"),
                        font_size =  font_size)
      } else {
        tab %>% kable(caption=title, digits = digits, booktabs=TRUE,...) %>%
          kable_styling(full_width = F, position = "center", 
                        latex_options = c("striped", "condensed", "HOLD_position","scale_down"),
                        font_size =  font_size)
      }
    }
  }
} else {
  mykable <- function(tab, transp = FALSE, digits = 2, title=NULL, font_size = NULL, ...){
    if(transp){
      tab %>% t() %>% kable(caption=title, digits = digits,...) %>%
        kable_styling(full_width = F, position = "center",
                      bootstrap_options = c("striped", "condensed"))  
    } else {
      tab %>% kable(caption=title, digits = digits, ...) %>%
        kable_styling(full_width = F, position = "center",
                      bootstrap_options = c("striped", "condensed"))
    }
  }
}

make_structure_table <- function(df, df_nan = NULL) {
  "Description. Return a table to describe dataframe strucuture & missing data."
  
  if (is.null(df_nan) == T){
    df_nan <- df %>% freq.na()
  }
  
  tab <- data.frame(
    Variable = names(df), 
    Class = sapply(df, function(x) class(x)[1]), 
    first_vals = sapply(df, function(x) paste0(head(x),  collapse = ", ")), 
    row.names = NULL
  )
  
  colnames(tab)[3] <- "First values"
  
  df_nan <- df_nan %>% rownames_to_column(var = "Variable")
  tab <- inner_join(x = tab, y = df_nan, by = "Variable")
  
  return(tab)
  
}

# Plots -------------------------------------------------------------------

make_pct_countplot <- function(df = dat_cat, var_name, color = "blue"){
  "Description. Return % countplot for a categorical variable."
  
  d <- dat_cat %>% 
    group_by_(var_name) %>% 
    summarize(freq = n()) %>% 
    mutate() %>% 
    mutate(pct = round(100 * freq / sum(freq), 2)) %>% 
    mutate(!!var_name := !!sym(var_name) %>% as.factor()) %>% 
    as.data.frame()
  
  d[[var_name]] <- fct_reorder(d[[var_name]], d$pct, .desc = T)
  
  plot_ly(data = d) %>%
    add_trace(
      x = ~.data[[var_name]], 
      y = ~.data[["pct"]], 
      marker = list(color = color), 
      type = "bar", 
      showlegend = F) %>% 
    
    layout(title = var_name, 
           xaxis = list(title = "", tickangle = -45), 
           yaxis = list(title = "%"))
  
}

make_histogram <- function(df = dat_quanti, var_name, density = T, thresold = NULL, color = "blue"){
  "Description. Return histogram plot with optional kernel density line."
  
  if (!is.null(thresold)) {
    df <- df %>%
      filter(!!sym(var_name) <= thresold)
  }
  
  p <- df %>% 
    ggplot(mapping = aes(x = !!sym(var_name), y = ..density..)) + 
    geom_histogram(bins = 50, 
                   fill = color, 
                   color = "white", 
                   alpha = .8) 
  
  if (density == T) {
    p <- p +
      geom_density(color = color) 
  }
  
  p <- p +
    labs(x = "", title = var_name) 
  
  ggplotly(p)
  
}

# Statistics  ------------------------------------------------------------------

stat_table <- function(x, var_name = "") {
  "Description. Return summary statistics for quantitative variable"
  
  na_freq <- 100 * sum(is.na(x)) / length(x)
  
  mean_x <- mean(x, na.rm = T)
  std_x <- sd(x, na.rm = T)
  quants <- quantile(x = x, na.rm = T) 
  stat_table <- data.frame(Moyenne = mean_x, 
                           std = std_x, 
                           Min = quants[1], 
                           q1 = quants[2], 
                           q2 = quants[3], 
                           q3 = quants[4], 
                           Max = quants[5], 
                           nans = na_freq)
  
  colnames(stat_table)[c(2, 4:6, 8)] <- c("Ecart-type", "Q25%", "Q50%", "Q75%", "% NA")
  rownames(stat_table) <- var_name
  
  return(stat_table)
}

hampel_filter <- function(x) {
  "Description. Compute Hampel filter to identify outliers."
  
  bound <- 3 * mad(x, constant = 1, na.rm = T)
  med_x <- median(x, na.rm = T)
  
  outliers <- which(x < med_x - bound | x > med_x + bound)
  
  return(outliers)
  
}
