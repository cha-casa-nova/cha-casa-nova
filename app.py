import os
import hmac
from datetime import datetime, timezone

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from sqlalchemy import update, inspect

from config import Config
from models import db, Guest, Gift


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_PERMANENT"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

        tabelas = inspect(db.engine).get_table_names()

        if "guests" in tabelas:
            colunas_guest = {
                coluna["name"]
                for coluna in inspect(db.engine).get_columns("guests")
            }

            if "gift_id" not in colunas_guest:
                with db.engine.begin() as conexao:
                    conexao.exec_driver_sql(
                        "ALTER TABLE guests ADD COLUMN gift_id INTEGER "
                        "REFERENCES gifts(id)"
                    )

       
        db.session.execute(
            update(Gift).values(reserved_by=None)
        )

        db.session.execute(
            update(Guest).values(gift_id=None)
        )

        db.session.commit()

        
        if Gift.query.count() == 0:
            cozinha = [
                "Jogo de pratos",
                "Jogo de copos",
                "Jogo de talheres",
                "Jogo de xícaras",
                "Jogo de panelas",
                "Frigideira antiaderente",
                "Panela de pressão",
                "Assadeira",
                "Travessa para servir",
                "Potes para mantimentos",
                "Potes herméticos",
                "Escorredor de louça",
                "Escorredor de macarrão",
                "Tábua de corte",
                "Jogo de facas",
                "Kit de utensílios de cozinha",
                "Ralador de alimentos",
                "Jarra para água",
                "Garrafa térmica",
                "Jogo de panos de prato",
            ]

            banheiro = [
                "Jogo de toalhas de banho",
                "Jogo de toalhas de rosto",
                "Tapete para banheiro",
                "Lixeira para banheiro",
                "Dispenser para sabonete líquido",
                "Kit de acessórios para banheiro",
                "Porta-escovas de dentes",
                "Cesto organizador",
                "Prateleira para banheiro",
                "Cortina para box",
                "Rodo para box",
                "Escova sanitária",
                "Dispenser para shampoo",
                "Jogo de toalhas de piso",
                "Organizador de gaveta para banheiro",
            ]

            quarto = [
                "Jogo de cama de casal",
                "Travesseiros",
                "Protetor de colchão",
                "Edredom de casal",
                "Manta para cama",
                "Kit de almofadas decorativas",
                "Cortina para quarto",
                "Tapete para quarto",
                "Abajur de cabeceira",
                "Espelho decorativo",
                "Relógio de parede",
                "Vaso decorativo",
                "Planta decorativa",
                "Quadro decorativo",
                "Organizador de roupas",
            ]

            sala = [
                "Air fryer",
                "Ventilador",
                "Aspirador de pó",
                "Sanduicheira elétrica",
                "Cafeteira elétrica",
                "Liquidificador",
                "Batedeira",
                "Micro-ondas",
                "Ferro de passar roupa",
                "Tábua de passar roupa",
                "Filtro ou purificador de água",
                "Luminária para sala",
                "Manta para sofá",
                "Kit de capas para almofadas",
                "Cesto organizador para sala",
            ]

            grupos = [
                (cozinha, "Cozinha", "#F3D879"),
                (banheiro, "Banheiro", "#C9E4C0"),
                (quarto, "Quarto e decoração", "#F4E8D0"),
                (sala, "Sala e eletrodomésticos", "#242424"),
            ]

            presentes_iniciais = []

            for itens, categoria, cor in grupos:
                for nome_presente in itens:
                    presentes_iniciais.append(
                        Gift(
                            name=nome_presente,
                            category=categoria,
                            color=cor,
                        )
                    )

            db.session.add_all(presentes_iniciais)
            db.session.commit()

  
    @app.route("/")
    def home():
        lista_presentes = Gift.query.order_by(
            Gift.category,
            Gift.name,
        ).all()

        return render_template(
            "index.html",
            lista_presentes=lista_presentes,
        )

    @app.route("/confirmar", methods=["POST"])
    def confirmar():
        nome = request.form.get("nome", "").strip()
        presenca = request.form.get("presenca", "").strip()
        acompanhantes_texto = request.form.get(
            "acompanhantes", "0"
        ).strip()

        if not nome or len(nome) > 100:
            flash(
                "Informe seu nome (até 100 caracteres).",
                "erro",
            )
            return redirect(url_for("home"))

        if presenca not in ("sim", "nao"):
            flash(
                "Selecione se você poderá comparecer.",
                "erro",
            )
            return redirect(url_for("home"))

        try:
            acompanhantes = int(acompanhantes_texto)
        except (TypeError, ValueError):
            acompanhantes = -1

        if acompanhantes < 0 or acompanhantes > 20:
            flash(
                "Informe uma quantidade de acompanhantes entre 0 e 20.",
                "erro",
            )
            return redirect(url_for("home"))

        if presenca == "nao":
            acompanhantes = 0

        gift_id_texto = request.form.get(
            "presente_id", ""
        ).strip()

        presente_surpresa = (
            request.form.get("presente_surpresa") == "sim"
        )

        try:
            if presenca == "sim" and gift_id_texto:
                try:
                    gift_id = int(gift_id_texto)
                except (TypeError, ValueError):
                    flash(
                        "O presente selecionado é inválido.",
                        "erro",
                    )
                    return redirect(url_for("home"))

                resultado = db.session.execute(
                    update(Gift)
                    .where(
                        Gift.id == gift_id,
                        Gift.reserved_at.is_(None),
                    )
                    .values(
                        reserved_at=datetime.now(timezone.utc),
                        reserved_by=None,
                    )
                )

                if resultado.rowcount != 1:
                    db.session.rollback()
                    flash(
                        "Esse presente já foi reservado. "
                        "Escolha outro ou confirme sem presente.",
                        "erro",
                    )
                    return redirect(url_for("home"))

            convidado = Guest(
                name=nome,
                attendance=presenca,
                companions=acompanhantes,
                gift_id=None,
            )

            db.session.add(convidado)
            db.session.commit()

            if presenca == "nao":
                mensagem = (
                    "Resposta registrada. Obrigado por avisar. 💗"
                )
            elif gift_id_texto:
                mensagem = (
                    "Presença e presente registrados com sucesso! 💗"
                )
            elif presente_surpresa:
                mensagem = (
                    "Presença confirmada! Obrigado; sua surpresa "
                    "será muito bem-vinda. 💗"
                )
            else:
                mensagem = (
                    "Presença confirmada com sucesso! Você pode "
                    "escolher um presente depois, se desejar. 💗"
                )

            flash(mensagem, "sucesso")

        except Exception:
            db.session.rollback()
            app.logger.exception(
                "Erro ao salvar confirmação ou reserva."
            )
            flash(
                "Não foi possível salvar sua resposta. Tente novamente.",
                "erro",
            )

        return redirect(url_for("home"))

    # Página de presentes
    @app.route("/presentes")
    def presentes():
        lista_presentes = Gift.query.order_by(
            Gift.category,
            Gift.name,
        ).all()

        return render_template(
            "presentes.html",
            presentes=lista_presentes,
        )

    # Reserva anônima de presente
    @app.route("/reservar/<int:gift_id>", methods=["POST"])
    def reservar(gift_id):
        try:
            resultado = db.session.execute(
                update(Gift)
                .where(
                    Gift.id == gift_id,
                    Gift.reserved_at.is_(None),
                )
                .values(
                    reserved_at=datetime.now(timezone.utc),
                    reserved_by=None,
                )
            )

            if resultado.rowcount != 1:
                db.session.rollback()
                flash(
                    "Esse presente já foi reservado ou não está disponível.",
                    "erro",
                )
            else:
                db.session.commit()
                flash(
                    "Presente reservado com sucesso! 💛",
                    "sucesso",
                )

        except Exception:
            db.session.rollback()
            app.logger.exception("Erro ao reservar presente.")
            flash(
                "Não foi possível realizar a reserva. Tente novamente.",
                "erro",
            )

        return redirect(url_for("presentes"))

    
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if session.get("admin_autenticado"):
            return redirect(url_for("admin"))

        if request.method == "POST":
            senha_digitada = request.form.get("senha", "")
            senha_correta = os.getenv("ADMIN_PASSWORD", "")

            if (
                senha_correta
                and hmac.compare_digest(
                    senha_digitada,
                    senha_correta,
                )
            ):
                session.clear()
                session.permanent = False
                session["admin_autenticado"] = True

                return redirect(url_for("admin"))

            flash(
                "Senha incorreta. Confira a senha configurada.",
                "erro",
            )

        return render_template("admin_login.html")

    
    @app.route("/admin")
    def admin():
        if not session.get("admin_autenticado"):
            return redirect(url_for("admin_login"))

        convidados = Guest.query.order_by(
            Guest.id.desc()
        ).all()

        confirmados = [
            pessoa for pessoa in convidados
            if pessoa.attendance == "sim"
        ]

        recusas = [
            pessoa for pessoa in convidados
            if pessoa.attendance == "nao"
        ]

        total_pessoas = sum(
            1 + (pessoa.companions or 0)
            for pessoa in confirmados
        )

        presentes_reservados = Gift.query.filter(
            Gift.reserved_at.isnot(None)
        ).order_by(
            Gift.category,
            Gift.name,
        ).all()

        return render_template(
            "admin.html",
            convidados=convidados,
            confirmados=len(confirmados),
            recusas=len(recusas),
            total_pessoas=total_pessoas,
            presentes_reservados=presentes_reservados,
        )

   
    @app.route(
        "/admin/excluir-convidado/<int:convidado_id>",
        methods=["POST"],
    )
    def excluir_convidado(convidado_id):
        if not session.get("admin_autenticado"):
            return redirect(url_for("admin_login"))

        try:
            convidado = db.session.get(Guest, convidado_id)

            if convidado is None:
                flash(
                    "Essa confirmação não foi encontrada.",
                    "erro",
                )
                return redirect(url_for("admin"))

            db.session.delete(convidado)
            db.session.commit()

            flash(
                "Confirmação excluída com sucesso!",
                "sucesso",
            )

        except Exception:
            db.session.rollback()
            app.logger.exception("Erro ao excluir confirmação.")
            flash(
                "Não foi possível excluir a confirmação.",
                "erro",
            )

        return redirect(url_for("admin"))


    @app.route(
        "/admin/liberar-presente/<int:gift_id>",
        methods=["POST"],
    )
    def liberar_presente(gift_id):
        if not session.get("admin_autenticado"):
            return redirect(url_for("admin_login"))

        try:
            presente = db.session.get(Gift, gift_id)

            if presente is None:
                flash(
                    "Esse presente não foi encontrado.",
                    "erro",
                )
                return redirect(url_for("admin"))

            if presente.reserved_at is None:
                flash(
                    "Esse presente já está disponível.",
                    "erro",
                )
                return redirect(url_for("admin"))

            presente.reserved_at = None
            presente.reserved_by = None

            db.session.commit()

            flash(
                f'O presente "{presente.name}" foi liberado!',
                "sucesso",
            )

        except Exception:
            db.session.rollback()
            app.logger.exception("Erro ao liberar presente.")
            flash(
                "Não foi possível liberar o presente.",
                "erro",
            )

        return redirect(url_for("admin"))

    
    @app.route("/admin/sair", methods=["POST"])
    def admin_sair():
        session.clear()
        return redirect(url_for("home"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
