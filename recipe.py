# ingredients = ['3 tablespoons vegetable oil, divided', '⅓ cup mixed nuts (cashews, pistachios, almonds)',
#                '1 medium onion, grated', '½ teaspoon garlic paste', '½ teaspoon ginger paste',
#                '1 (8 ounce) can tomato sauce', '1 teaspoon cayenne pepper', '½ teaspoon ground turmeric',
#                '2 teaspoons ground coriander', '1 teaspoon garam masala', '1 cup water', '¼ cup raisins',
#                '½ cup chopped carrots', '½ cup chopped green bell pepper', '½ cup chopped fresh green beans',
#                '½ cup green peas', '1 cup chopped potatoes', '4 ounces paneer, cubed', '¼ cup milk',
#                '¼ cup heavy cream', 'salt to taste']
#
# ingredients2 = ['4 cloves garlic', '1 (1 inch) piece fresh ginger', '2 tablespoons vegetable oil', '2  bay leaves',
#                 '1 (1 inch) piece cinnamon stick', '1 teaspoon coriander seeds', '6  whole black peppercorns',
#                 '4 pods green cardamom', '4  whole cloves', '1 large onion, minced', '1\u2009½ teaspoons salt, divided',
#                 '1  green chile pepper, cut into matchsticks', '2  tomatoes, diced',
#                 '½ cup water, if needed  (Optional)', '2 teaspoons chili powder', '1 teaspoon ground cumin',
#                 '2 tablespoons butter', '1 teaspoon ground fenugreek (menthi powder)',
#                 '1  russet potato, cut into 1/2-inch cubes', '½ pound paneer, cut into 1/2-inch cubes',
#                 '½ cup frozen peas', '2 teaspoons honey']
#
# ingredients3 = ['2  potatoes, peeled', '1 cup paneer cheese, grated  (Optional)', '2 teaspoons cornstarch',
#                 '2 teaspoons ground cumin', '2 teaspoons cayenne pepper', '1 teaspoon salt', 'vegetable oil for frying',
#                 '8  cashews  (Optional)', '¼ cup water  (Optional)', '1 tablespoon vegetable oil',
#                 '1  green chile pepper, chopped', '½ teaspoon ginger-garlic paste', '½ teaspoon cumin seed',
#                 '1  onion, grated', '¼ cup tomato puree', '2teaspoons ground coriander', '1 teaspoon salt',
#                 '1 teaspoon garam masala', '¼ teaspoon ground turmeric', '¼ teaspoon cayenne pepper',
#                 '¼ cup heavy whipping cream', '¼ cup milk', '2 tablespoons water, or as needed  (Optional)']
#
# ingredients4 = ['4  skinless, boneless chicken breast halves', 'salt and freshly ground black pepper to taste',
#                 '2  eggs', '1 cup panko bread crumbs, or more as needed', '½ cup grated Parmesan cheese',
#                 '2 tablespoons all-purpose flour, or more if needed', '1 cup olive oil for frying',
#                 '½ cup prepared tomato sauce', '¼ cup fresh mozzarella, cut into small cubes',
#                 '¼ cup chopped fresh basil', '½ cup grated provolone cheese', '¼ cup grated Parmesan cheese',
#                 '1 tablespoon olive oil']
#
# ingredients5 = ['oil for deep frying', '1 cup unbleached all-purpose flour', '2 teaspoons salt',
#                 '½ teaspoon ground black pepper', '½ teaspoon cayenne pepper', '¼ teaspoon garlic powder',
#                 '½ teaspoon paprika', '1  egg', '1 cup milk',
#                 '3  skinless, boneless chicken breasts, cut into 1/2-inch strips', '¼ cup hot pepper sauce',
#                 '1 tablespoon butter']





import spacy, re

nlp = spacy.load('en_core_web_sm')

def _filter(token):
    if len(token) < 2:
        return False
    if token.is_stop:
        return False
    if token.is_digit:
        return False
    if token.like_num:
        return False
    return True

def getProcessedIngredients(ingredient):
    blacklist = ["cup", "teaspoon", "teaspoons", "cups", "tablespoons", "tablespoon", "medium", "large", "small",
                 "ounce",
                 "ounces", "cube", "cubes", "inch", "inches", "pound", "pounds", "cubed", "piece", "pieces", "halves"]

    ingredient = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", ingredient)
    # ingredient = ingredient.split(",")[0]
    var = nlp(ingredient)
    ingr = []
    for token in var:
        if str(token) not in blacklist and _filter(token):
            ingr.append(str(token))
        # print(token, token.tag_, token.pos_, spacy.explain(token.tag_))
    return ingr
