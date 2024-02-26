from nestipy.common.templates.generator import TemplateGenerator

gen = TemplateGenerator()

result = gen.render_template('controller.txt', name='Test')
print(result)