
from app import create_app
from models import db, Guest, Gift

app = create_app()

with app.app_context():
    total_confirmacoes = Guest.query.count()

    total_reservados = Gift.query.filter(
        Gift.reserved_at.isnot(None)
    ).count()

    print(f"\nConfirmações no painel: {total_confirmacoes}")
    print(f"Presentes reservados: {total_reservados}")
    print(f"Total de presentes: {Gift.query.count()}")

    resposta = input(
        "\nIsso apagará todas as confirmações e liberará todos os presentes.\n"
        "Digite APAGAR para confirmar: "
    )

    if resposta == "APAGAR":
        try:
            Guest.query.delete(synchronize_session=False)

            Gift.query.update(
                {
                    Gift.reserved_by: None,
                    Gift.reserved_at: None,
                },
                synchronize_session=False,
            )

            db.session.commit()

            print("\nTudo certo!")
            print("Confirmações apagadas.")
            print("Todos os presentes foram liberados.")
            print(f"Presentes preservados: {Gift.query.count()}")

        except Exception as erro:
            db.session.rollback()
            print(f"\nErro: {erro}")
            print("As alterações foram canceladas.")

    else:
        print("\nOperação cancelada. Nenhum dado foi alterado.")
