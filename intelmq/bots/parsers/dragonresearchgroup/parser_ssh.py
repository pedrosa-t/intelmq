from intelmq.lib.bot import Bot, sys
from intelmq.lib.message import Event
from intelmq.lib.harmonization import DateTime
from intelmq.lib import utils

class DragonResearchGroupSSHParserBot(Bot):

    def process(self):
        report = self.receive_message()

        if not report.contains("raw"):
            self.acknowledge_message()

        raw_report = utils.base64_decode(report.value("raw"))
        for row in raw_report.split('\n'):

            row = row.strip()

            self.logger.error("Raw row %s" % row)

            if len(row) == 0 or row.startswith('#'):
                continue
            
            splitted_row = row.split('|')
            event = Event()

            columns = ["source.asn", "source.as_name", "source.ip", "time.source"]
            
            for key, value in zip(columns, splitted_row):
                value = value.strip()
                
                if key == "time.source":
                    value += " UTC"
                
                event.add(key, value, sanitize=True)

            time_observation = DateTime().generate_datetime_now()
            event.add('time.observation', time_observation, sanitize=True)
            event.add('feed.name', u'dragonresearchgroup')
            event.add('feed.url', u'http://dragonresearchgroup.org/insight/sshpwauth.txt')
            event.add('classification.type', u'brute-force')
            event.add('protocol.application', u'ssh')
            event.add("raw", row, sanitize=True)
            
            self.send_message(event)
        self.acknowledge_message()
   

if __name__ == "__main__":
    bot = DragonResearchGroupSSHParserBot(sys.argv[1])
    bot.start()