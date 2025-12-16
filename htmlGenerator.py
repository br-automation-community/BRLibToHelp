from datatypes import Function, FunctionBlock
from pathlib import Path


class FunctionBlockHtmlGenerator:
    """Shared HTML generator for function block diagrams used by both libraryToPng and libraryToChm."""
    
    def __init__(self):
        pass
    
    def generate_fub_diagram_html(self, fb: Function | FunctionBlock) -> str:
        """Generate the HTML for a function block diagram (the visual representation)."""
        return self.generate_fub_table(fb)
    
    def generate_fub_table(self, fb: Function | FunctionBlock) -> str:
        """Generate the complete function block table HTML."""
        content = f"""
        <table id="fub" cellspacing="0" class="fubLayout">
            {self.generate_fub_top_border()}
            {self.generate_table_header(fb)}"""
        
        # Orange part (var_input and var_output)
        if isinstance(fb, FunctionBlock) and max(len(fb.var_input), len(fb.var_output)) or isinstance(fb, Function):
            content += f"""
            <tr>
                {self.generate_table_datatype_in(fb)}
                {self.generate_table_in(fb)}
                {self.generate_table_out(fb)}
                {self.generate_table_datatype_out(fb)}
            </tr>"""
        
        # White part (var_in_out)
        if len(fb.var_in_out) > 0:
            content += f"""
            <tr>
                {self.generate_in_out_table_datatype_in(fb)}
                {self.generate_in_out_table_in_out(fb)}
                {self.generate_in_out_table_datatype_out(fb)}
            </tr>"""
        
        content += f"""
            {self.generate_fub_bottom_border()}
        </table>"""
        
        return content
    
    def generate_in_out_table_datatype_in(self, fb: Function | FunctionBlock) -> str:
        """Generate the left datatype column for IN_OUT variables."""
        content = f"""
                <td class="fubDataTypeIn">
                    <table class="fubData">"""
        
        for var in fb.var_in_out:
            if var.is_reference:
                type_str = f"&{var.type}"
            else:
                type_str = var.type
            content += f"""
                        <tr>
                            <td class="fubElementRight">{type_str}</td>
                            <td width="10">
                                <hr width="20px" size="1" color="#000000">
                            </td>
                        </tr>"""
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def generate_in_out_table_datatype_out(self, fb: Function | FunctionBlock) -> str:
        """Generate the right datatype column for IN_OUT variables."""
        content = f"""
                <td class="fubDataTypeOut">
                    <table class="fubData">"""
        
        for var in fb.var_in_out:
            if var.is_reference:
                type_str = f"&{var.type}"
            else:
                type_str = var.type
            content += f"""
                        <tr>
                            <td width="10">
                                <hr width="20px" size="1" color="#000000">
                            </td>
                            <td class="fubElementLeft">{type_str}</td>
                        </tr>"""
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def generate_in_out_table_in_out(self, fb: Function | FunctionBlock) -> str:
        """Generate the center column for IN_OUT variable names."""
        content = f"""
                <td colspan="2" class="fubInOut">
                    <table>"""
        
        for var in fb.var_in_out:
            content += f"""
                        <tr>
                            <td class="fubElementCenter">{var.name}</td>
                        </tr>"""
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def generate_fub_top_border(self) -> str:
        """Generate the top border row of the function block."""
        return f"""
            <tr>
                <td></td>
                <td class="fubTop"></td>
                <td class="fubTop"></td>
                <td></td>
            </tr>"""
    
    def generate_fub_bottom_border(self) -> str:
        """Generate the bottom border row of the function block."""
        return f"""
            <tr>
                <td></td>
                <td class="fubBottom"></td>
                <td class="fubBottom"></td>
                <td></td>
            </tr>"""
    
    def generate_table_header(self, fb: Function | FunctionBlock) -> str:
        """Generate the header row with the function/function block name."""
        return f"""
            <th class="fubDataTypeIn"></th>
            <th colspan="2" class="fubGradBlue">{fb.name}</th>
            <th class="fubDataTypeOut"></th>"""
    
    def generate_table_datatype_in(self, fb: Function | FunctionBlock) -> str:
        """Generate the left datatype column for input variables."""
        content = f"""
                <td class="fubDataTypeIn">
                    <table class="fubData">"""
        
        for var in fb.var_input:
            if var.is_reference:
                type_str = f"&{var.type}"
            else:
                type_str = var.type
            content += f"""
                        <tr>
                            <td class="fubElementRight">{type_str}</td>
                            <td width="10">
                                <hr width="20px" size="1" color="#000000">
                            </td>
                        </tr>"""
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def generate_table_in(self, fb: Function | FunctionBlock) -> str:
        """Generate the input variables column."""
        content = f"""
                <td class="fubGradOrange1">
                    <table class="fubIn">"""
        
        for var in fb.var_input:
            content += f"""
                        <tr>
                            <td class="fubElementLeft">{var.name}</td>
                        </tr>"""
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def generate_table_out(self, fb: Function | FunctionBlock) -> str:
        """Generate the output variables column."""
        content = f"""
                <td class="fubGradOrange2">
                    <table class="fubOut">"""
        if isinstance(fb, FunctionBlock):
            for var in fb.var_output:
                content += f"""
                        <tr>
                            <td class="fubElementRight">{var.name}</td>
                        </tr>"""
        else:
            content += f"""
                        <tr>
                            <td class="fubElementRight">return</td>
                        </tr>"""
        
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def generate_table_datatype_out(self, fb: Function | FunctionBlock) -> str:
        """Generate the right datatype column for output variables."""
        content = f"""
                <td class="fubDataTypeOut">
                    <table class="fubData">"""
        if isinstance(fb, FunctionBlock):
            for var in fb.var_output:
                content += f"""
                        <tr>
                            <td width="10">
                                <hr width="20px" size="1" color="#000000">
                            </td>
                            <td class="fubElementLeft">{var.type}</td>
                        </tr>"""
        else:
            content += f"""
                    <tr>
                        <td width="10">
                            <hr width="20px" size="1" color="#000000">
                        </td>
                        <td class="fubElementLeft">{fb.return_type}</td>
                    </tr>"""
        
        content += f"""
                    </table>
                </td>"""
        
        return content
    
    def get_style_content(self) -> str:
        """Read and return the CSS style content from the css/style.css file."""
        style_path = Path(__file__).parent.resolve()
        style_path = style_path / "css/style.css"
        with open(style_path.as_posix(), "r") as f:
            file_content = f.read()
        return file_content
    
    def generate_style_section(self) -> str:
        """Generate the <style> section with the CSS content."""
        style_content = self.get_style_content()
        return f'\t<style type="text/css">\n{style_content}\n\t</style>'
