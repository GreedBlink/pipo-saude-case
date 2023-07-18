library(shiny)
library(shinydashboard)
library(shinydashboardPlus)
library(reactable)


conn = DBI::dbConnect(RSQLite::SQLite(),'../pipo_database.db')

specialties = DBI::dbGetQuery(conn, 'select * from specialties')

specialties_opt = specialties$specialty_denormalized_name
names(specialties_opt) = specialties$specialty_name

# Definindo a interface do usuário
ui <- dashboardPage(
  header = dashboardHeader(
    title = "Pipo Saúde"
  ),
  sidebar = dashboardSidebar(
    sidebarMenu(
      menuItem("Buscar prestador", tabName = "buscar", icon = icon("search"))
    )
  ),
  body = dashboardBody(
    tabItems(
      tabItem(
        tabName = "buscar",
        h2("Buscar Prestador"),
        shiny::wellPanel(
          shiny::fluidRow(
            shiny::column(
              width = 3,
              shiny::selectInput(
                inputId = 'specialty',
                label = 'Especialidade',
                selected = 'Clínica médica',
                choices= specialties_opt
              )
            ),
            shiny::column(
              width = 3,
              shiny::radioButtons(
                inputId = 'remote',
                label = 'Teleatendimento',
                choices = list("Sim" = T, "Não" = F), 
                selected = F,inline = T
              )
            ),
            shiny::column(
              width = 3,
              shiny::radioButtons(
                inputId = 'weekend',
                label = 'Atendimento final de semana',
                choices = list("Sim" = T, "Não" = F), 
                selected = F,
                inline = T
              )
            ),
            shiny::column(
              width = 3,
              shiny::numericInput(
                inputId = 'n_results',
                label = 'Quantidade',
                value = 10,
                min = 10,
                max=50
              )
            ),
          shiny::column(
            width = 12, 
            shiny::actionButton('search','pesquisar')
          )
          
             
          )
          
        ),
        reactable::reactableOutput('providerList')
        # Adicione aqui os elementos de interface do usuário para buscar prestadores
      )
    )
  )
)

# Definindo o servidor
server <- function(input, output) {
  # Adicione aqui a lógica do servidor para buscar prestadores
  
  
  observeEvent(input$search,{
    
    
    data = DBI::dbGetQuery(
      conn = conn, 
      glue::glue("
            with spc as (
            	select 
            	provider_id,
            	group_concat(specialty_name) as ar_specialty,
            	group_concat(specialty_denormalized_name) as ar_specialty_dn
            	
            	from provider_specialties
            	left join specialties 
            	on provider_specialties.specialty_id=specialties.specialty_id
            	group by provider_id
            ), final as (
            
            	select * from health_provider 
            	left join provider_score 
            	on  health_provider.provider_id = provider_score.provider_id
            	left  join spc on health_provider.provider_id = spc.provider_id
            
            	
            )
            
            select * from final

        ")
    )
    
    
    data = data |>  dplyr::filter(
      stringr::str_detect(ar_specialty_dn,input$specialty)
    ) |> 
      dplyr::filter(online_service == input$remote) |> 
      dplyr::filter(weekend_service == input$weekend)
    
    
    output$providerList <- reactable::renderReactable({
      reactable::reactable( 
        data |> dplyr::select(provider_name,zip_code, score, ar_specialty) |> 
          dplyr::arrange(desc(score))
       )
    })
    
  })
 
  
}

# Executando o aplicativo
shinyApp(ui, server)
