"""Dessine le graphe d'attaques d'un système d'argumentation (fichier .apx).

Usage : python visualize.py tests/data/test_af1.apx [--output graphe.png]
"""
import argparse
import re

import matplotlib.pyplot as plt
import networkx as nx


def parse_file(file_path):
    arguments = set()
    attacks = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("arg("):
                match = re.match(r"arg\((\w+)\)", line)
                if match:
                    arguments.add(match.group(1))
            elif line.startswith("att("):
                match = re.match(r"att\((\w+),(\w+)\)", line)
                if match:
                    attacks.append((match.group(1), match.group(2)))

    return arguments, attacks


def draw_argumentation_graph(arguments, attacks, output=None):
    # Créer un graphe orienté
    graph = nx.DiGraph()

    # Ajouter les arguments comme nœuds
    graph.add_nodes_from(arguments)

    # Ajouter les attaques comme arêtes
    graph.add_edges_from(attacks)

    # Configurer le dessin
    pos = nx.layout.spring_layout(graph)
    plt.figure(figsize=(8, 6))

    # Dessiner les nœuds
    nx.draw_networkx_nodes(graph, pos, node_size=1000, node_color='lightblue')

    # Dessiner les étiquettes des nœuds
    nx.draw_networkx_labels(graph, pos, font_size=12, font_color='black', font_weight='bold')

    # Dessiner les arêtes (attaques)
    for edge in graph.edges:
        reverse_edge = (edge[1], edge[0])
        if reverse_edge in graph.edges:
            # Si une attaque mutuelle existe, dessiner une flèche courbée
            nx.draw_networkx_edges(graph, pos, edgelist=[edge], arrowstyle='-|>', edge_color='black',
                                   connectionstyle='arc3,rad=0.2', node_size=1200)
        else:
            nx.draw_networkx_edges(graph, pos, edgelist=[edge], arrowstyle='-|>', edge_color='black',
                                   node_size=1200)

    plt.title("Graphe d'argumentation", fontsize=15)
    plt.axis("off")
    if output:
        plt.savefig(output, bbox_inches="tight")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Affiche le graphe d'un système d'argumentation.")
    parser.add_argument("file", help="fichier .apx décrivant le système")
    parser.add_argument("--output", help="enregistrer l'image au lieu de l'afficher")
    args = parser.parse_args()

    arguments, attacks = parse_file(args.file)
    draw_argumentation_graph(arguments, attacks, args.output)


if __name__ == "__main__":
    main()
