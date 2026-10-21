# Twin Bee Enhanced (MSX2): el parche IPS, sus comprobaciones y la web.
# Pon tu volcado de Twin Bee en la raiz como twinbee.rom.
ROM  ?= twinbee.rom
IPS  := ips/twinbee_enhanced_msx2.ips
WORK := work

.PHONY: all comprueba aplica verifica test web
all: test web

comprueba:              # es tu ROM la de Twin Bee que espera el parche
	@python3 -c "import hashlib,sys; h=hashlib.sha256(open('$(ROM)','rb').read()).hexdigest(); print(h); sys.exit(h!='02bdce8ceafe6af05a45b61a689e78807551df663afd152090f7cd9cac827dd4')"

aplica: comprueba       # la ROM mejorada en work/
	mkdir -p $(WORK)
	python3 tools/ips.py aplica $(ROM) $(IPS) $(WORK)/twinbee_enhanced_msx2.rom

verifica:               # aplica el parche a tu volcado y comprueba el resultado
	python3 tools/verifica.py $(ROM)

test:
	python3 -m unittest discover -s tests -v

web:
	python3 tools/md2html.py docs en
	python3 tools/md2html.py docs/es es
	python3 tools/check_enlaces.py docs
