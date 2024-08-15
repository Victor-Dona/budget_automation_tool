# categories.py
import pandas as pd

category_keywords = {
    'Groceries': [
        'gourmeats', 'arrocha', 'super', 'super xtra', 'rey', 'pricesmart', 'metro', 
        'riba', 'verduras', 'vegetales', 'full market', 'vida y salud mini mark',
        'snack', 'yogurt',
        # San Francisco, California
        'wholefds'
    ],
    'Eating Out': [
        # Coffee
        'coffee', 'cafe unido', 'siete granos', 'starbucks', 'local', 'latte', 'cafe',
        'cappuccino', 'deli gourmet',
        # Sweet
        'palettamerica', 'saint honore', 'frostberry',
        # Alhocol
        'la rana dorada', 'ranazo', 'cerveceria central', 'legitima', 'taphouse', 'buena vista taphouse',
        'beermarkt', 'istmo brew rest', 'casa bruja', 'capital gastrobar',
        # Pizza
        'little caesars',
        'granier', 'comida china', 'golden', 'jugos pica fruta', 'la vaquita,', 'artisana',
        'norexpress', 'vietnam cuisin',

        # Venezuelan
        'don tiriton', 'comida venezolana',

        'nachitos', 'nachos', 'emparedado', 'pho', 'galletas deliciosas', 'mini waffles',
        'raspado', 'platanitos', 'relato', 'unido', 'postre', 'alitas', 'takitos', 
        'shawarma', 'burger', 'jot dog', 'tandoori', 'taquitos', 'hotel el ejecutivo', 
        'kokeshi', 'nacion', 'sangria', 'french toast',
        'ajisen', 'fitheart', 'bbq', 'oh my burger', 'zaz', 'arnazen do cafe',  
        'michaels', 'hung s center', 'rokamadour', 'pasteleria', 'wendys', 'almuerzo', 
        'gelarti', 'cakefit', 'chicken', 'gongcha', 'pa que nelson',
        'casa de hampao', 'burger king', 'mentiritas blancas', 'beauty y the butcher', 
        'el huekito mexicano', 'gelato', 'dairy queen', 'la strega', 'perejil', 'miss cho', 
        'macdonalds', 'grand deli gourmet', 'izakaya', 'fratelli', 'the raj', 'ay mi negra', 
        'the wallace', 'queso chela', 'moocha', 'pedidosya', 'www.pidepaya.com', 'am pm', 
        'casa santa', 'anti burger', 'tacos la neta', 'vitali', 'segundo muelle', 
        'souvlaki gr', 'golden unicorn', 'los tacos', 'subway', 'esa flaca rica', 'food', 
        'sushi', 'tea', 'pizza', 'rest', 'pizzeria', 'tip', 'mo mo', 'ramen', 'CAFE BILAL', 
        'rock and folk', 'bistro', 'xing fu tang', 'athanasiou', 'arepadictos',
        'wahaka', 'poke', 'cafe', 'los tarascos', 'popeyes', 'brew', 
        'mcdonalds', 'taco bell', 'restaurante', 'bakery', 'patisserie', 
        'onze', 'chocolatish', 'sushark', 'athens', 'delicia', 'empanada',
        'masala indian cuisine', 'kitchen', 'frappe', 'blue moon', 'uber eats', 'piza',
        # San Francisco, California
        'the melt', 'curry leaf', 'the grove', 'lapisara', 'mels drive in', 'crab house',
        'tst  24th and mission', 'boudin bakery', 'starbucks int arr sfo', 'ghirardelli',
        'souvlakisazo', 'chai latte', 'petit paris', 
    ],
    'Clothes': [
        'velez', 'bershka', 'old navy', 'bananarepublic', 'hm', 'zara multiplaza', 'steven', 'adidas',
        'express mp'
    ],
    'Utilities': [
        # Gas
        'terpel', 'delta', 'texaco', 'gasolina', 'puma',
        # Cleaning
        'super klin', 'lavanderia', 'prontowash', 'carwash',
        # Internet & Data
        'liberty', 'cwp', 'tigo', 'mi tigo', 'recarga telefonia',
        'internet',
        # Insurance
        'sura', 'assa',
        # Others
        'supera', 'estacion', 'ena corredores', 'ena sur'
    ],
    'Subscriptions': [
        'APPLE.COM', 'spotify', 'google', 'paypal  microsoft', 'pickup music', 'kindle svcs',
        'amazon prime', 'kindle unltd', 'datacamp', 'duolingo'
    ],
    'Entertainment': [
        'burke bikes', 'cinepolis', 'bolos', 'toque', 'summer fest', 'cine', 'escape room', 'centro deportivo billa',
        'macrofest', 'pa vacilar', 'selina casco viejo', 'mieventos api',
    ],
    'Transportation': [
        'uber', 'ubr', 'taxi'
    ],
    'Other Expenses': [
        # Government
        'municipio de panama', 'alcaldia', 'hatillo',
        # Parking spaces
        'est multiplaza fideico', 'edificio ph royal cent',
        'seguro de fraude', 'roja parajoda', 'lanyard', 'stanford univ', 
        'aliss', 'discovery', 'innovacion', 'relojin', 'amzn', 'apple store', 
        'xiaomi', 'panafoto', 'limpoint', 'mumuso', 'parking', 'cc scotiabank prom', 
        'permisos de trabajo', 'mona cell', 'WL *VUE*Testing Exam', 'fund tecnologica de pm', 
        'aliss', 'do it center', 'novey', 'amazon mktplace', 'hidrodent', 
        'sastre', 'copago',
        # Flowers
        'silvaticaflores', 'flores',
        # Plants
        'vivero castillo', 'planta', 'casa philodendron',
        # Envios
        'mybox express'
    ],
    'Health': [
        'power club', 'orto', 'farmas', 'javillo', 'revilla', 'centro medico', 'optirex', 
        'optica', 'farma', 'corromaduro', 'natalia corro de la guardia', 'minimed'
    ],
    'Personal care': [
        'barber', 'corte', 'barba', 'sandro rodriguez', 'facial'
    ],
    'Traveling': [
        'copa air', 'airbnb', 
    ],
    'Pets': [
        'melo', 'american pets', 'centro veterinario', 'comida bebelines', 'heno', 'conejitos'
    ],
    'Cashback': [
        'cashback'
    ],
    'Rent': [
    ],
    'Education': [
    ],
    'Books': [
        'libreria', 'amazon prime pmts'
    ],
    'Loans': [
    ],
    'Internal Transfer': [
        'BANCA EN LINEA TRANSFERENCIA', 'BANCA MOVIL THE BANK OF NOVA SCOTIA', 'retiro cuenta de ahorro',
        'atm-banco general', 'entre cuentas', 'vuelto', 'atm deposito', 'savings', 'profuturo',
        'su pago recibido gracias', 
        # Transferencias entre cuentas
        #'reversa por rechazos', 
        'reversa'
    ],
    'Salary': [
        'ACH - COMPANIA PANAMEN', 
    ],
    'Interests': [
        'interes cuenta de ahorros'
    ],
    'Tech Purchases': [
        'apple device panama', 'ishop', 'rjk solutions'
    ],
    'Unexpected Events': [
        'accidente', 'emparche de llanta'
    ],
    'Credit Cards': [
        'interes financiado del periodo', 'cobro admtvo. por mora', 'scotiabank prom   (plazo cuota', 
        'itbms cargo membresia', 'impuesto seguro fraude', 'cargo anual tarjeta clave',
    ],
    'Sold Item': [
    ]
}

# Flatten the dictionary
# keyword_to_category = {keyword: category for category, keywords in category_keywords.items() for keyword in keywords}


def categorize(description):
    if pd.isna(description):
        return 'Uncategorized'
    description_lower = description.lower()
    for category, keywords in category_keywords.items():
        if any(keyword.lower() in description_lower for keyword in keywords):
            return category
    return 'Uncategorized'
