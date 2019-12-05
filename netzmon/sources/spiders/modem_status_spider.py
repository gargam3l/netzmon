from netzmon.sources import items
from netzmon.sources import config
import scrapy




class ModemStatusSpider(scrapy.Spider):
    name = "modem_status"

    def start_requests(self):
        return [scrapy.FormRequest(config.MODEM_LOGIN_POST_URL,
                                   formdata={config.MODEM_LOGIN_USERNAME_KEY: config.MODEM_LOGIN_USERNAME_VALUE,
                                             config.MODEM_LOGIN_PASSWORD_KEY: config.MODEM_LOGIN_PASSWORD_VALUE},
                                   callback=self.login)]

    def parse(self, response):
        pass

    def login(self, response):
        self.logger.info("Successfully logged in!")
        connection_url = config.MODEM_STATUS_PAGE_URL
        yield scrapy.Request(connection_url, callback=self.read_connection_data)

    def read_connection_data(self, response):
        self.logger.info("Connection status page opened.")
        table_dict = {}
        table_list = response.xpath("//table")
        # Iterating through the 5 tables present on the page
        for table in table_list:
            headers = table.xpath("./tr//th|./th")
            header_name_list = []
            table_name = ""
            for header in headers:
                header_name = header.xpath(".//script/text()").get().lstrip("i18n(\"").rstrip("\")")
                # Some headers are actually table titles, so need the ability to exclude them from the column headers
                add_header = True

                # Adding distinct table names for each table
                if header_name == "Startup Procedure":
                    table_name = "Modem status"
                    add_header = False
                elif header_name == "Downstream Bonded Channels":
                    table_name = "Downstream Bonded Channels"
                    add_header = False
                elif header_name == "Total Correctables":
                    table_name = "Correctable totals"
                elif header_name == "Upstream Bonded Channels":
                    table_name = "Upstream Bonded Channels"
                    add_header = False
                elif header_name == "CM IP Address":
                    table_name = "IP addressing"

                if add_header:
                    header_name_list.append(header_name)

            rows = table.xpath("./tr")
            table_content = []
            # Parse each row in the table
            for row in rows:
                row_content_list = []
                columns = row.xpath("./td")
                # Parse each cell in the row
                for column in columns:
                    cell_content = column.xpath("string(.|.//script/text())")
                    cell_text = ""
                    if len(cell_content) > 0:
                        cell_text = cell_content.get()
                        # Some cells contain unneccessary parts, hence stripping those out
                        if cell_text.find('i18n') != -1:
                            cell_text = cell_text.lstrip("i18n(\"").rstrip("\")")
                        # Or substituting with empty string
                        elif cell_text == '\xa0':
                            cell_text = ''
                        if cell_text == '':
                            cell_text = " "
                    row_content_list.append(cell_text)

                if len(row_content_list) > 0:
                    # Full join (cartesian product) of the header list and the row content
                    # Key - header name, value: cell value
                    row_content_dict = dict(zip(header_name_list, row_content_list))
                    # Remove unnecessary entries
                    if table_name == "Downstream Bonded Channels":
                        del row_content_dict["Lock Status"]
                        del row_content_dict["Modulation"]
                        del row_content_dict["Channel ID"]
                    elif table_name == "Upstream Bonded Channels":
                        del row_content_dict["Lock Status"]
                        del row_content_dict["US Channel Type"]
                        del row_content_dict["Channel ID"]
                    add_header = False

                    # Add the dictionary to the list of rows for the specific table
                    table_content.append(row_content_dict)
            # Add table content for each 'table_name' as key
            table_dict[table_name] = table_content
            self.logger.info("Parsed following table: %s", table_name)
        # Yield the gathered data
        modem_data = items.ModemConnectionDetails()
        modem_data['modem_status'] = table_dict['Modem status']
        modem_data['ds_channel_list'] = table_dict['Downstream Bonded Channels']
        modem_data['correctable_summary'] = table_dict['Correctable totals']
        modem_data['us_channel_list'] = table_dict['Upstream Bonded Channels']
        modem_data['timestamp'] = config.timestamp()
        yield modem_data
        # Logout from the modem
        yield scrapy.Request(config.MODEM_LOGOUT_URL)
        self.logger.info("Successfully logged out!")
