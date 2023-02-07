
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
  tab <- left_join(x = tab, y = df_nan, by = "Variable")
  
  return(tab)
  
}

# Plots -------------------------------------------------------------------

make_pct_countplot <- function(df, var_name, color = "lightblue"){
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

make_histogram <- function(
    df, 
    var_name, 
    density = T, 
    color = "lightblue"){
  "Description. Return histogram plot with optional kernel density line."
  
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
  
  if (var_name == "valeur_fonciere") {
    p <- p + 
      scale_x_continuous(labels = unit_format(unit = "K", scale = 1e-3)) 
  }
  
  ggplotly(p)
  
}

make_scatter_plot <- function(df, x_var, y_var, color = "orange"){
  "Description. Make plotly scatterplot and compute Pearson correlation coef."
  
  corr <- cor(x = df %>% pull(x_var), 
              y = df %>% pull(y_var))
  
  title <- paste("Corr =", round(corr, 2), "| n =", format(nrow(df), scientific = F, big.mark = " "))
  
  p <- df %>% 
    ggplot(mapping = aes_string(x = x_var, y = y_var)) +
    geom_point(color = color, size = .6) +
    geom_smooth() +
    ggtitle(label = title)
  
  if (y_var == "valeur_fonciere") {
    p <- p + 
      scale_y_continuous(labels = unit_format(unit = "K", scale = 1e-3)) 
  }
  
  ggplotly(p)
  
}

distribution_per_category <- function(df, by, target,  multiple = F) {
  "Description. Draw quantitative variable distribution per category."
  
  if (multiple == F) {
    show_legend <- T
    
    p <- df %>% 
      ggplot(mapping = aes_string(x = target, 
                                  y = "..density..", 
                                  color = by, 
                                  fill = by)) +
      geom_histogram(bins = 30, alpha = .4) +
      xlab("")
  }
  
  else {
    show_legend <- FALSE 
    wrapper <- as.formula(paste("~", by)) 
    
    p <- df %>% 
      ggplot(mapping = aes_string(x = target, y = "..density..", color = by)) +
      geom_histogram(bins = 30, fill = "white") +
      facet_wrap(wrapper)
    
  }
  
  if (target == "valeur_fonciere") {
    p <- p + 
      scale_x_continuous(labels = unit_format(unit = "K", scale = 1e-3)) 
  }
  
  p <- p + ggtitle(label = paste(target, "vs", by))
  
  if (show_legend) {
    p <-  ggplotly(p) %>% 
      layout(legend = list(orientation = "h", title = ""))
  }
  
  else {
    p <- ggplotly(p) %>% layout(showlegend = F) 
  }
  
  return(p)
  
}

boxplot_per_category <- function(df, target, by) {
  "Description. Boxplot of target variable depending on category."
  
  p <- df %>%
    ggplot(mapping = aes(x = reorder(!!sym(by), -!!sym(target)), 
                         y = !!sym(target), 
                         color = reorder(!!sym(by), -!!sym(target)), 
                         fill = reorder(!!sym(by), -!!sym(target))))  +
    geom_boxplot(alpha = .3) 
  
  if (target == "valeur_fonciere") {
    p <- p +
      scale_y_continuous(labels = unit_format(unit = "K", scale = 1e-3)) 
  }
    
  p <- p +
    labs(title = paste(target, "selon", by), 
         x = "", 
         y = "") +
    theme(axis.text.x = element_text(angle = -90))
  
  ggplotly(p) %>% layout(showlegend = F)
  
}

barplot_per_category <- function(df, cat_var1, cat_var2) {
  "Description. Categorical variable countplot per category of other categorical variable."
  
  p <- df %>%
    ggplot() +
    geom_bar(
      mapping = aes_string(
        x = cat_var1, 
        color = cat_var2, 
        fill = cat_var2), 
      alpha = .5) +
    labs(x = "", title = cat_var1) +
    theme(axis.text.x = element_text(angle = -90))
  
  ggplotly(p) %>%
    layout(legend = list(orientation = "h", y = -.5))
  
}


# Data handling  ------------------------------------------------------------------

draw_samples <- function(df, n_samples = 10000){
  "Description. Draw n_subset non-NANs data points."
  
  df_no_nans <- df %>% na.omit()
  n_samples <- min(n_samples, nrow(df_no_nans))
  
  ids <- sample(x = rownames(df_no_nans), size = n_samples, replace = F)
  df_subset <- df_no_nans %>% filter(rownames(.) %in% ids)
  
  return(df_subset)
}

# Statistics  ------------------------------------------------------------------

stat_table <- function(x, var_name = "") {
  "Description. Return summary statistics for quantitative variable"
  
  na_freq <- sum(is.na(x)) / length(x)
  n_available <- length(x) * (1 - na_freq)
  
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
                           nans = 100 * na_freq, 
                           N = n_available)
  
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
