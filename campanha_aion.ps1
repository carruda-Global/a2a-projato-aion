param(
    [string]$Acao = "completo",
    [string]$Keywords = "engenheiro producao compliance lgpd",
    [string]$Industria = "engineering construction manufacturing",
    [int]$Limite = 25
)

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

switch ($Acao) {
    "completo" {
        Write-Output "=== CAMPANHA AION - MAQUINA DE VENDAS COMPLETA ==="
        Write-Output "1. Prospectando no LinkedIn..."
        python -m aion.main --sales prospect --sales-input "{"""keywords""":"""$Keywords""","""industry""":"""$Industria""","""limit""":$Limite,"""auto_create_deals""":true}"
        
        Write-Output ""
        Write-Output "2. Pipeline atual:"
        python -m aion.main --sales pipeline
        
        Write-Output ""
        Write-Output "3. Leads prontos para site:"
        python -c "
from aion.sales.database import SessionLocal, init_db
from aion.sales import models
init_db()
db = SessionLocal()
leads = db.query(models.Lead).filter(models.Lead.score >= 60).order_by(models.Lead.score.desc()).all()
print(f'Total leads qualificados: {len(leads)}')
for l in leads:
    print(f'  {l.name:20s} | {l.company:20s} | Score: {l.score}/100 | {l.title}')
db.close()
" 2>&1
    }
    
    "prospectar" {
        Write-Output "=== PROSPECTANDO LINKEDIN ==="
        python -m aion.main --sales prospect --sales-input "{"""keywords""":"""$Keywords""","""industry""":"""$Industria""","""limit""":$Limite,"""auto_create_deals""":true}"
    }
    
    "pipeline" {
        Write-Output "=== PIPELINE DE VENDAS ==="
        python -m aion.main --sales pipeline
    }
    
    "leads" {
        python -c "
from aion.sales.database import SessionLocal, init_db
from aion.sales import models
init_db()
db = SessionLocal()
leads = db.query(models.Lead).filter(models.Lead.score >= 60).order_by(models.Lead.score.desc()).all()
print(f'=== LEADS QUALIFICADOS (>=60): {len(leads)} ===')
for l in leads:
    print(f'{l.name};{l.company};{l.title};{l.score};{l.location};{l.linkedin_url}')
db.close()
" 2>&1
    }
    
    "outreach" {
        Write-Output "=== GERANDO OUTREACH PARA SITE ==="
        python -c "
from aion.sales.database import SessionLocal, init_db
from aion.sales import models, outreach
init_db()
db = SessionLocal()
leads = db.query(models.Lead).filter(models.Lead.score >= 60).limit(5).all()
for l in leads:
    msg = outreach.generate_linkedin_message({'name':l.name,'company':l.company,'industry':l.industry},
        'conhecer o EcoSystem AION - 59 agentes de IA gratis por 15 dias')
    email = outreach.generate_email_content({'name':l.name,'company':l.company,'industry':l.industry,'email':l.email},
        'testar o EcoSystem AION gratuitamente')
    print(f'--- {l.name} ({l.company}) ---')
    print(f'LinkedIn: {msg}')
    print(f'Email: {email[\"subject\"]}')
    print(f'URL: https://global-engenharia.com/ecosystem')
    print()
db.close()
" 2>&1
    }
}
