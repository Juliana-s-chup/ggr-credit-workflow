#!/usr/bin/env python
"""
Script de lancement des tests avec couverture.
Usage: python run_tests.py [options]
"""
import sys
import os
import subprocess


def run_command(cmd, description):
    """ExÃ©cute une commande et affiche le rÃ©sultat."""
    print(f"\n{'='*70}")
    print(f"ðŸ§ª {description}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"\nâŒ Ã‰CHEC: {description}")
        return False
    else:
        print(f"\nâœ… SUCCÃˆS: {description}")
        return True


def main():
    """Fonction principale."""
    print("\n" + "=" * 70)
    print("ðŸš€ LANCEMENT DE LA SUITE DE TESTS COMPLÃˆTE")
    print("=" * 70)

    results = []

    # 1. Tests unitaires Django
    results.append(run_command("python manage.py test --verbosity=2", "Tests unitaires Django"))

    # 2. Tests avec pytest et couverture
    results.append(
        run_command(
            "pytest --cov=suivi_demande --cov=analytics --cov-report=html --cov-report=term-missing",
            "Tests pytest avec couverture",
        )
    )

    # 3. VÃ©rification de la couverture minimale
    results.append(
        run_command("coverage report --fail-under=75", "VÃ©rification couverture >= 75%")
    )

    # 4. GÃ©nÃ©ration du rapport HTML
    results.append(run_command("coverage html", "GÃ©nÃ©ration rapport HTML"))

    # RÃ©sumÃ© final
    print("\n" + "=" * 70)
    print("ðŸ“Š RÃ‰SUMÃ‰ DES TESTS")
    print("=" * 70)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"\nâœ… Tests rÃ©ussis: {passed}/{total}")
    print(f"âŒ Tests Ã©chouÃ©s: {failed}/{total}")

    if failed == 0:
        print("\nðŸŽ‰ TOUS LES TESTS SONT PASSÃ‰S !")
        print(f"\nðŸ“„ Rapport de couverture: htmlcov/index.html")
        return 0
    else:
        print("\nâš ï¸  CERTAINS TESTS ONT Ã‰CHOUÃ‰")
        return 1


if __name__ == "__main__":
    sys.exit(main())
