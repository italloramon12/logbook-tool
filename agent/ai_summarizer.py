#!/usr/bin/env python3
# agent/ai_summarizer.py
"""
Módulo para gerar resumos inteligentes das atividades diárias usando IA.
Suporta Ollama (local) ou OpenAI API.
"""
import time
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from db import fetch_events

logging.basicConfig(level=logging.INFO)

class ActivitySummarizer:
    def __init__(self, use_ollama=True):
        """
        Args:
            use_ollama: Se True, usa Ollama local. Se False, usa OpenAI API.
        """
        self.use_ollama = use_ollama
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not use_ollama and not self.openai_api_key:
            logging.warning("OpenAI API key not found. Set OPENAI_API_KEY env variable.")
    
    def get_daily_activities(self, date: Optional[datetime] = None) -> List[Dict]:
        """Obtém todas as atividades de um dia específico"""
        if date is None:
            date = datetime.now()
        
        # Início e fim do dia
        day_start = int(datetime(date.year, date.month, date.day, 0, 0, 0).timestamp())
        day_end = day_start + 86400
        
        rows = fetch_events(day_start, day_end, limit=10000)
        
        activities = []
        for r in rows:
            activities.append({
                "id": r[0],
                "timestamp": r[1],
                "type": r[2],
                "title": r[3] or "",
                "detail": r[4] or "",
                "duration": r[5] or 0
            })
        
        return activities
    
    def categorize_activities(self, activities: List[Dict]) -> Dict:
        """Categoriza atividades automaticamente"""
        categories = {
            "work": {"time": 0, "apps": []},
            "communication": {"time": 0, "apps": []},
            "entertainment": {"time": 0, "apps": []},
            "productivity": {"time": 0, "apps": []},
            "social_media": {"time": 0, "apps": []},
            "development": {"time": 0, "apps": []},
            "idle": {"time": 0, "apps": []},
            "other": {"time": 0, "apps": []}
        }
        
        # Palavras-chave para categorização
        keywords = {
            "work": ["office", "excel", "word", "powerpoint", "docs", "sheets", "slides", "email", "calendar"],
            "communication": ["whatsapp", "telegram", "discord", "slack", "teams", "zoom", "meet", "skype", "messages"],
            "entertainment": ["youtube", "netflix", "spotify", "twitch", "video", "music", "game"],
            "productivity": ["notion", "evernote", "trello", "asana", "jira", "todoist", "notes"],
            "social_media": ["facebook", "twitter", "instagram", "linkedin", "reddit", "tiktok"],
            "development": ["vscode", "code", "terminal", "github", "gitlab", "stackoverflow", "python", "javascript", "git"]
        }
        
        for activity in activities:
            title_lower = activity["title"].lower()
            detail_lower = activity["detail"].lower()
            duration = activity["duration"]
            typ = activity["type"]
            
            # Idle tem prioridade
            if typ == "idle" or "ocioso" in title_lower:
                categories["idle"]["time"] += duration
                categories["idle"]["apps"].append(activity["title"])
                continue
            
            # Tenta categorizar por palavras-chave
            categorized = False
            for category, words in keywords.items():
                if any(word in title_lower or word in detail_lower for word in words):
                    categories[category]["time"] += duration
                    categories[category]["apps"].append(activity["title"])
                    categorized = True
                    break
            
            if not categorized:
                categories["other"]["time"] += duration
                categories["other"]["apps"].append(activity["title"])
        
        # Remove duplicatas e conta ocorrências
        for cat in categories.values():
            app_counts = {}
            for app in cat["apps"]:
                app_counts[app] = app_counts.get(app, 0) + 1
            cat["apps"] = [{"name": app, "count": count} for app, count in 
                          sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return categories
    
    def generate_summary_ollama(self, activities: List[Dict], categories: Dict) -> str:
        """Gera resumo usando Ollama"""
        try:
            import requests
            
            # Prepara contexto
            total_time = sum(cat["time"] for cat in categories.values())
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            # Top 10 atividades
            activity_times = {}
            for act in activities:
                title = act["title"]
                if title not in activity_times:
                    activity_times[title] = 0
                activity_times[title] += act["duration"]
            
            top_activities = sorted(activity_times.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Monta prompt
            prompt = f"""Você é um assistente que analisa atividades diárias de um usuário.

RESUMO DO DIA:
- Tempo total monitorado: {hours}h {minutes}min

DISTRIBUIÇÃO POR CATEGORIA:
"""
            for cat_name, cat_data in categories.items():
                if cat_data["time"] > 0:
                    cat_hours = cat_data["time"] // 3600
                    cat_mins = (cat_data["time"] % 3600) // 60
                    prompt += f"- {cat_name.title()}: {cat_hours}h {cat_mins}min\n"
            
            prompt += "\nTOP 10 ATIVIDADES:\n"
            for title, duration in top_activities:
                dur_h = duration // 3600
                dur_m = (duration % 3600) // 60
                prompt += f"- {title}: {dur_h}h {dur_m}min\n"
            
            prompt += """
Baseado nesses dados, gere um resumo estruturado do dia contendo:

1. **Resumo Geral**: Uma visão geral do dia (2-3 frases)
2. **Produtividade**: Avaliação de produtividade (0-10) e justificativa
3. **Principais Atividades**: Destaques do que o usuário fez
4. **Sugestões**: 2-3 sugestões práticas para melhorar a rotina
5. **Insights**: Observações interessantes sobre os padrões de uso

Seja objetivo, amigável e construtivo. Responda em português brasileiro.
"""
            
            # Chama Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",  # ou outro modelo instalado
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Erro ao gerar resumo")
            else:
                logging.error(f"Ollama error: {response.status_code}")
                return self.generate_summary_fallback(categories, top_activities, hours, minutes)
                
        except Exception as e:
            logging.error(f"Error with Ollama: {e}")
            return self.generate_summary_fallback(categories, top_activities, hours, minutes)
    
    def generate_summary_openai(self, activities: List[Dict], categories: Dict) -> str:
        """Gera resumo usando OpenAI API"""
        try:
            import openai
            
            if not self.openai_api_key:
                return self.generate_summary_fallback(categories, [], 0, 0)
            
            openai.api_key = self.openai_api_key
            
            # Prepara dados
            total_time = sum(cat["time"] for cat in categories.values())
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            activity_times = {}
            for act in activities:
                title = act["title"]
                if title not in activity_times:
                    activity_times[title] = 0
                activity_times[title] += act["duration"]
            
            top_activities = sorted(activity_times.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Monta mensagem
            context = f"Tempo total: {hours}h {minutes}min\n\nCategorias:\n"
            for cat_name, cat_data in categories.items():
                if cat_data["time"] > 0:
                    cat_hours = cat_data["time"] // 3600
                    cat_mins = (cat_data["time"] % 3600) // 60
                    context += f"- {cat_name}: {cat_hours}h {cat_mins}min\n"
            
            context += "\nTop atividades:\n"
            for title, duration in top_activities[:5]:
                dur_h = duration // 3600
                dur_m = (duration % 3600) // 60
                context += f"- {title}: {dur_h}h {dur_m}min\n"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente que analisa atividades diárias e fornece insights úteis em português brasileiro."},
                    {"role": "user", "content": f"{context}\n\nGere um resumo estruturado com: resumo geral, avaliação de produtividade (0-10), principais atividades, e 2-3 sugestões de melhoria."}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error with OpenAI: {e}")
            return self.generate_summary_fallback(categories, top_activities, hours, minutes)
    
    def generate_summary_fallback(self, categories: Dict, top_activities: List, hours: int, minutes: int) -> str:
        """Gera um resumo básico sem IA quando APIs não estão disponíveis"""
        summary = f"# 📊 Resumo do Dia\n\n"
        summary += f"**Tempo total monitorado:** {hours}h {minutes}min\n\n"
        
        summary += "## 📈 Distribuição por Categoria\n\n"
        for cat_name, cat_data in sorted(categories.items(), key=lambda x: x[1]["time"], reverse=True):
            if cat_data["time"] > 0:
                cat_hours = cat_data["time"] // 3600
                cat_mins = (cat_data["time"] % 3600) // 60
                percentage = (cat_data["time"] / (hours * 3600 + minutes * 60)) * 100 if hours + minutes > 0 else 0
                summary += f"- **{cat_name.replace('_', ' ').title()}**: {cat_hours}h {cat_mins}min ({percentage:.1f}%)\n"
        
        summary += "\n## 🏆 Top Atividades\n\n"
        for i, (title, duration) in enumerate(top_activities[:5], 1):
            dur_h = duration // 3600
            dur_m = (duration % 3600) // 60
            summary += f"{i}. {title}: {dur_h}h {dur_m}min\n"
        
        # Análise simples de produtividade
        work_time = categories.get("work", {}).get("time", 0) + categories.get("development", {}).get("time", 0) + categories.get("productivity", {}).get("time", 0)
        total_active = sum(cat["time"] for cat in categories.values()) - categories.get("idle", {}).get("time", 0)
        
        if total_active > 0:
            productivity_score = int((work_time / total_active) * 10)
            summary += f"\n## 💯 Score de Produtividade: {productivity_score}/10\n\n"
            
            if productivity_score >= 7:
                summary += "✅ Excelente! Você manteve bom foco em atividades produtivas.\n"
            elif productivity_score >= 4:
                summary += "⚠️ Dia moderado. Há espaço para melhorar o foco em atividades produtivas.\n"
            else:
                summary += "❌ Dia pouco produtivo. Considere organizar melhor seu tempo.\n"
        
        return summary
    
    def generate_daily_summary(self, date: Optional[datetime] = None) -> str:
        """Gera o resumo completo do dia"""
        activities = self.get_daily_activities(date)
        
        if not activities:
            return "# Nenhuma atividade registrada hoje\n\nO monitoramento pode não estar ativo ou nenhuma atividade foi detectada."
        
        categories = self.categorize_activities(activities)
        
        if self.use_ollama:
            ai_summary = self.generate_summary_ollama(activities, categories)
        elif self.openai_api_key:
            ai_summary = self.generate_summary_openai(activities, categories)
        else:
            ai_summary = ""
        
        # Se não temos resumo de IA, usa fallback
        if not ai_summary or "erro" in ai_summary.lower():
            return self.generate_summary_fallback(
                categories, 
                sorted([(a["title"], a["duration"]) for a in activities], 
                       key=lambda x: x[1], reverse=True)[:10],
                sum(cat["time"] for cat in categories.values()) // 3600,
                (sum(cat["time"] for cat in categories.values()) % 3600) // 60
            )
        
        return ai_summary


def main():
    """Gera resumo do dia atual"""
    print("🤖 Gerando resumo do dia...\n")
    
    # Tenta usar Ollama primeiro
    summarizer = ActivitySummarizer(use_ollama=True)
    summary = summarizer.generate_daily_summary()
    
    print(summary)
    
    # Salva em arquivo
    output_dir = os.path.expanduser("~/.activity_tracker")
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(output_dir, f"summary_{today}.md")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n💾 Resumo salvo em: {output_file}")


if __name__ == "__main__":
    main()
