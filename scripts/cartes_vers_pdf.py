from PIL import Image
import os

# --- CONFIGURATION GÉNÉRALE ---
DOSSIER_CARTES = "images"
IMAGE_BACK = "back.png"
FICHIER_SORTIE = "cartes_sang_d_encre.pdf"

# --- FORMAT DU DOCUMENT ---
DPI = 300  # résolution
MM_TO_PX = lambda mm: int(mm / 25.4 * DPI)

A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
A4_WIDTH_PX = MM_TO_PX(A4_WIDTH_MM)
A4_HEIGHT_PX = MM_TO_PX(A4_HEIGHT_MM)

# --- MISE EN PAGE DES CARTES ---
NB_COLONNES = 3
NB_LIGNES = 4
NB_PAR_PAGE = NB_COLONNES * NB_LIGNES

ESPACE_ENTRE_CARTES_MM = 5     # espace horizontal/vertical entre les cartes
ESPACE_PX = MM_TO_PX(ESPACE_ENTRE_CARTES_MM)

# --- TAILLE DES CARTES ---
UTILISER_TAILLE_FIXE_MM = True  # True = fixe, False = automatique

if UTILISER_TAILLE_FIXE_MM:
    TAILLE_CARTE_MM = 63
    CARTE_PX = MM_TO_PX(TAILLE_CARTE_MM)
    TAILLE_CARTE = (CARTE_PX, CARTE_PX)
else:
    carte_width = (A4_WIDTH_PX - (NB_COLONNES + 1) * ESPACE_PX) // NB_COLONNES
    carte_height = (A4_HEIGHT_PX - (NB_LIGNES + 1) * ESPACE_PX) // NB_LIGNES
    TAILLE_CARTE = (carte_width, carte_height)

# --- CHARGEMENT DES IMAGES ---

# Faces
cartes_face = [
    os.path.join(DOSSIER_CARTES, f)
    for f in sorted(os.listdir(DOSSIER_CARTES))
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
]

# Dos
try:
    image_back = Image.open(IMAGE_BACK).convert("RGBA").resize(TAILLE_CARTE)
except Exception as e:
    print(f"Erreur de chargement du dos : {e}")
    exit()

# --- Préparation des images recto-verso ---
toutes_images = []

for f in cartes_face:
    filename = os.path.basename(f).lower()
    img = Image.open(f).convert("RGBA").resize(TAILLE_CARTE)
    toutes_images.append(img)  # face

    # Cas spéciaux → double face (pas de dos)
    if filename in ["lettre.png", "vote_force.png"]:
        toutes_images.append(img.copy())  # seconde face identique
    else:
        toutes_images.append(image_back.copy())  # dos normal


# --- CRÉATION DES PAGES ---
def creer_page(images):
    page = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), color=(255, 255, 255))
    for idx, img in enumerate(images):
        col = idx % NB_COLONNES
        row = idx // NB_COLONNES
        if row >= NB_LIGNES:
            break
        x = ESPACE_PX + col * (TAILLE_CARTE[0] + ESPACE_PX)
        y = ESPACE_PX + row * (TAILLE_CARTE[1] + ESPACE_PX)
        page.paste(img, (x, y))
    return page

# Génération
pages = []

for i in range(0, len(toutes_images), NB_PAR_PAGE):
    batch = toutes_images[i:i + NB_PAR_PAGE]
    page = creer_page(batch)
    pages.append(page)

# Export PDF
if pages:
    pages[0].save(FICHIER_SORTIE, save_all=True, append_images=pages[1:], resolution=DPI, format='PDF')
    print(f"✅ PDF généré : {FICHIER_SORTIE}")
else:
    print("❌ Aucune carte à afficher.")
