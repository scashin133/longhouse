

import java.applet.Applet;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.StringTokenizer;
import java.util.NoSuchElementException;
import java.util.Vector;

/**
 * @version $Id: Chat.java,v 1.24 2004/07/27 02:38:10 halcy0n Exp $
 */
public class Chat extends Applet implements Runnable {
    private final static String DEFAULT_HELP_URL = "http://cookie.sorcery.net/~ircd_/help/";
    private final static String DEFAULT_LIST_URL = "http://www.valinor.sorcery.net/channels/";
    private final static String DEFAULT_FONT_NAME = "Monospace";
    private final static int DEFAULT_FONT_SIZE = 12;
    private final static String DEFAULT_QUIT_MESSAGE = "http://snirc.sourceforge.net/";
    private final static String DEFAULT_CHANNEL_NAME = "#help";
    private final static int DEFAULT_IRC_PORT = 6667;
    public static final char MODE_CHANOP = '@';
    public static final char MODE_NONE = ' ';
    public static final char MODE_VOICE = '+';
    private IRCConnection connection;
    private ChatUserInterface chat;
    private String[] allowedNicks;
    private String banMask;
    private Vector IgnoreList = new Vector();
    public final static String VERSION = "v1.0";

    private ActionListener userInputListener = new ActionListener() {
        public void actionPerformed(ActionEvent event) {
            TextField inputBox = (TextField) event.getSource();
            String s = inputBox.getText().trim();
            String chanTopic, topicChan, jumpedChanName, chanPass;
            if (s.length() == 0)
                return;

            if (!connection.isOpen()) {
                sendToUser("[E] Not connected to server");
                return;
            }

            if (s.startsWith("/")) {
                StringTokenizer cmd = new StringTokenizer(s);
                String command = cmd.nextToken().substring(1);
                if (command.equalsIgnoreCase("help")) {
                    showHelp();
		} else if (command.equalsIgnoreCase("ignore")) {
		    try {
			String com = cmd.nextToken();
			if(com.equalsIgnoreCase("add"))
			    addIgnore(extractEverythingAfter(s, com));
			else if(com.equalsIgnoreCase("remove")) {
			    try { 
				int index = Integer.parseInt(cmd.nextToken());

				if(index < 0 || index > (IgnoreList.size()-1)) {
				    throw new NumberFormatException();
				}

				remIgnore(index);
			    } catch(NumberFormatException ex) {
				sendToUser("[E] You specified an invalid index. Type, /ignore, to see valid indexes.");
			    }

			} else
			    sendToUser("[E] Correct syntax for /ignore is: /ignore [add|remove] [mask|index]");
		    }
		    catch(NoSuchElementException ex) {
			showIgnoreList();
		    }
                } else if (command.equalsIgnoreCase("list")) {
                    showChannelList();
                } else if (command.equalsIgnoreCase("notice")) {
                    String target = cmd.nextToken();
                    String text = extractEverythingAfter(s, target);
                    sendToUser("-<" + target + ">- " + text);
                    sendToServer("NOTICE " + target + " :" + text);
                } else if (command.equalsIgnoreCase("msg")) {
                    String target = cmd.nextToken();
                    String text = extractEverythingAfter(s, target);
                    sendToUser("*<" + target + ">* " + text);
                    sendToServer("PRIVMSG " + target + " :" + text);
                } else if (command.equalsIgnoreCase("raw")) {
                    sendToServer(extractEverythingAfter(s, command));
                } else if (command.equalsIgnoreCase("me")) {
                    sendToUser("* " + getCurrentNick() + " " + extractEverythingAfter(s, command));
                    sendToServer(
                            "PRIVMSG "
                            + getChannelName()
                            + " :\001ACTION "
                            + extractEverythingAfter(s, command)
                            + "\001");
                } else if (command.equalsIgnoreCase("join")) {
           
            /* if (! ServerChat.canChanChange) { 
              sendToUser("Feature disabled by website administrator \n");
              return;
              } else { */
            jumpedChanName = cmd.nextToken();
                if (!jumpedChanName.substring(0,1).equals("#")){
                 sendToUser("Valid channel names begin with # \n");
                  return;
                  } 
                  chanPass = s.substring(s.indexOf(jumpedChanName) + jumpedChanName.length());
                  sendToUser("* Joining " + jumpedChanName + "\n");
                 sendToServer( "PART " + getChannelName() + "\nJOIN " + jumpedChanName + chanPass);     
                
           		} else if (command.equalsIgnoreCase("topic")) {
           			topicChan = cmd.nextToken();
            		if (topicChan.substring(0,1).equals("#")){  
             			chanTopic = extractEverythingAfter(s, topicChan);
             			sendToServer("TOPIC " + topicChan + " :" + chanTopic);
          			} else {
            			chanTopic = extractEverythingAfter(s, topicChan);
             			sendToServer("TOPIC " + getChannelName() + " :" + chanTopic);
             		}
          		} else if (command.equalsIgnoreCase("part")) {
           			sendToUser("This command has been removed. Use /join to enter another channel");
           			return;
          	 	} else  {
                    sendToServer(extractEverythingAfter(s, "/"));
                }
        }else {
                sendToUser("<" + getCurrentNick() + "> " + s);
                sendToServer("PRIVMSG " + getChannelName() + " :" + s);
            }
            inputBox.setText("");
        }
    };

    private ActionListener buttonsAndMenuListener = new ActionListener() {
        public void actionPerformed(ActionEvent event) {
            String command = event.getActionCommand();
            if (command.equals("Help")) {
                showHelp();
            } else if (command.equals("List")) {
                showChannelList();
            } else if (command.equals("Nick")) {
                sendToServer("NICK " + EntryDialog.promptForNick());
            } else if (command.equals("Channel")) {
                String channel = EntryDialog.promptForChannel();
                sendToServer("PART " + getChannelName());
                sendToServer("JOIN " + channel);
            } else {
                String selectedNick = chat.getSelectedNick();
                if (selectedNick == null
                        && !command.equals("About")
                        && !command.equals("Refresh")) {
                    sendToUser("[*] You must first select a nickname by clicking on it.");
                } else {
                    if (command.equals("Whois")) {
                        sendToServer("WHOIS " + selectedNick);
                    } else if (command.equals("Ignore")) {
			banMask = "";
			sendToServer("USERHOST " + selectedNick);
			while (banMask == "") { } //We need to wait to recieve the data
			String ignore = EntryDialog.promptForBanmask(banMask);
			addIgnore(ignore);
		    } else if (command.equals("View Ignore List")){
		    	showIgnoreList();
		    }else if (command.equals("Give Ops")) {
			sendToServer("MODE " + getChannelName() + " +o "
				+ selectedNick);
		    } else if (command.equals("Take Ops")) {
			sendToServer("MODE " + getChannelName() + " -o "
				+ selectedNick);
		    } else if (command.equals("Give Voice")) {
			sendToServer("MODE " + getChannelName() + " +v "
				+ selectedNick);
		    } else if (command.equals("Take Voice")) {
			sendToServer("MODE " + getChannelName() + " -v "
				+ selectedNick);
		    } else if (command.equals("Kick")) {
			sendToServer("KICK " + getChannelName() + " "
				+ selectedNick + " :Bye");
		    } else if (command.equals("Ban")) {
			banMask = "";
		    	sendToServer("USERHOST " + selectedNick);
			while (banMask == "") { } //We need to wait a minute to recieve the data
			String ban = EntryDialog.promptForBanmask(banMask);
			sendToServer("MODE " + getChannelName() + " +b "
				+ ban);
                    } else if (command.equals("Refresh")) {
                        sendToServer("NAMES " + getChannelName());
                    } else if (command.equals("Version")) {
                        sendToServer(
                                "PRIVMSG "
                                + selectedNick
                                + " :\001VERSION\001");
                    } else if (command.equals("Ping")) {
                        sendToServer(
                                "PRIVMSG "
                                + selectedNick
                                + " :\001PING "
                                + System.currentTimeMillis()
                                + "\001");
                    } else if (command.equals("About")) {
                        sendToUser("[*] SorceryNet IRC ChatUserInterface Applet");
                        sendToUser("[*] Copyright (C) 1998-2000, Anthony F. Miller");
                        sendToUser("[*] Open Source under the BSD license");
                        sendToUser("[*] Report bugs and get updates at: http://sourceforge.net/projects/snirc/");
                    }
                }
            }
        }
    };

    public Chat() {
        Command.registerStrategies();
    }

    public void init() {
        this.allowedNicks = createAllowedNicks();
        setLayout(new GridLayout(1, 1));
        this.chat = new ChatUserInterface(userInputListener,
                buttonsAndMenuListener,
                !isBooleanParameterSet("defaultHideJoinsAndParts"),
                isBooleanParameterSet("Barebones"),
                isBooleanParameterSet("AllowChannelChange"),
                new Font(getTextParameter("FontName", DEFAULT_FONT_NAME),
                        Font.PLAIN,
                        getNumericParameter("FontSize", DEFAULT_FONT_SIZE)));
        this.add(chat, BorderLayout.CENTER);
    }

    /**
     * Cleanly kill the connection and terminate the applet. Inherited from Applet and called
     * by the Applet container.
     */
    public void stop() {
        connection.close(DEFAULT_QUIT_MESSAGE);
    }

    /**
     * Open the connection to the server. Inherited from Applet and called by the Applet container.
     */
    public void start() {
        this.connection = new IRCConnection(getTextParameter("Server", getDocumentBase().getHost()),
                getNumericParameter("Port", DEFAULT_IRC_PORT));
        new Thread(this).start();
    }
   

    public void clearNickList() {
        chat.getNickList().removeAll();
    }

    public void addToNickList(String nick, char modeChar) {
        String decoratedNick = modeChar + nick;
        for (int i = 0; i < chat.getNickList().getItemCount(); i++) {
            if (decoratedNick.compareTo(chat.getNickList().getItem(i)) >= 0) {
                chat.getNickList().add(decoratedNick, i);
                return;
            }
        }
        chat.getNickList().add(decoratedNick);
    }

    public void changeNickMode(String nick, char mode, boolean modeActive) {
        String decoratedNick = getDecoratedNickFromNickList(nick);

        if (decoratedNick == null) {
            addToNickList(nick, MODE_NONE);
            decoratedNick = MODE_NONE + nick;
        }

        if (modeActive) {
            if (mode == 'o') {
                replaceOnNickList(nick, nick, MODE_CHANOP);
            } else {
                if (decoratedNick.charAt(0) == MODE_NONE)
                    replaceOnNickList(nick, nick, MODE_VOICE);
            }
        } else {
            if (mode == 'o') {
                replaceOnNickList(nick, nick, MODE_NONE);
            } else {
                if (decoratedNick.charAt(0) != MODE_CHANOP)
                    replaceOnNickList(nick, nick, MODE_NONE);
            }
        }
	}
    
    /**
     * Sets the banMask based on the userhost info gathered from NamesNumericsStrategy
     */
     public void setBanMask(String banMsk){
     	banMask = banMsk;
     
     }

    private void connectToServer() {
        if (connection == null)
            throw new IllegalStateException("Can't connect to server - connection has not been initialised");
        try {
            /* Test for new parameter here... */
            String nick = getTextParameter("Nick", "");
            if (nick == "") {
              nick = EntryDialog.promptForNick();
            } 
            printClientIntro();
            setNick(nick);
            sendToUser(
                    "*** Attempting connection to "
                    + connection.getServerHostName()
                    + " on port "
                    + connection.getServerPortNumber());
            connection.connect();
            sendToUser(
                    "*** Connected!  Attempting handshaking, please stand by...");
            sendToServer("NICK " + getCurrentNick() + "\n");
            sendToServer("USER JavaClient dummy dummy :" + getDocumentBase().toString() + "\n");
        } catch (java.io.IOException e) {
            System.out.println("Unable to make connection to host");
            sendToUser("Sorry. Unable to make " + "connection to server.");
            connection.close();
        }
    }

    public void deleteFromNickList(String nick) {
        for (int i = 0; i < chat.getNickList().getItemCount(); i++) {
            if (chat.getNickList().getItem(i).substring(1).equals(nick)) {
                chat.getNickList().remove(i);
                return;
            }
        }
    }

    public boolean denyPrivateMessagesFrom(String source) {
        return isBooleanParameterSet("DenyPrivateMessages")
                && !isAServer(source) && !isAllowedNick(source);
    }

    public String getChannelName() {
        return chat.getChannelName();
    }

    public String getCurrentNick() {
        return chat.getNick();
    }

    public String getDecoratedNickFromNickList(String nick) {
        for (int i = 0; i < chat.getNickList().getItemCount(); i++) {
            if (chat.getNickList().getItem(i).substring(1).equals(nick)) {
                return chat.getNickList().getItem(i);
            }
        }

        return null;
    }

    public boolean isCurrentChannel(String channel) {
        return getChannelName().equalsIgnoreCase(channel);
    }

    public boolean isCurrentNick(String nick) {
        return getCurrentNick().equalsIgnoreCase(nick);
    }

    private void printClientIntro() {
        sendToUser(
                "******\n"
                + "*** Using SNirc Java Applet version: " + VERSION + "\n"
                + "*** Type /HELP for help on using the applet.\n"
                + "*** This applet is beta.  Address any problems to: cl00bie@flame.org\n"
                + "*** Web page authors are strongly encouraged to join the SNirc mailing list\n"
                + "*** By sending an e-mail to snirc-webmasters-request@lists.sourceforge.net\n"
                + "***   with \"subscribe\" (w/o quotes) in the subject, and following the instructions you are mailed.\n"
                + "******");
    }

    public void replaceOnNickList(
            String oldNick,
            String newNick,
            char newModeChar) {
        deleteFromNickList(oldNick);
        addToNickList(newNick, newModeChar);
    }

    public void run() {
        connectToServer();
        try {
            while (connection.isOpen()) {
                Command command = Command.parseLine(connection.readLine());
                if (command != null)
                    command.execute(this);
            }
        } catch (java.io.IOException ioe) {
            if (connection.isOpen()) {
                sendToUser("[E] Could not receive data from server. (" + ioe.getMessage() + ")");
                connection.close();
            }
        }

        sendToUser("[M] Disconnected");
    }

    public void sendToServer(String message) {
        try {
            connection.sendLine(message);
        } catch (java.io.IOException ex) {
            sendToUser("[E] Closing connection, could not send to server: " + ex.getMessage());
            connection.close();
        }
    }

    public void sendToUser(String message) {
        chat.appendOutputLine(message);
    }

    public void serverConnectionIsActive() {
        chat.makeReadyForCommands(isBooleanParameterSet("Barebones"));
        setChannelName(getTextParameter("Channel", DEFAULT_CHANNEL_NAME));
        if (getChannelName().equals(""))
            setChannelName(EntryDialog.promptForChannel());

        sendToServer("JOIN " + getChannelName());
    }

    public void setChannelName(String channelName) {
        chat.setChannelName(channelName);
    }

    public void setChannelTopic(String channelTopic) {
        chat.setTopic(channelTopic);
    }

    public void setNick(String nick) {
        chat.setNick(nick);
    }

    private void showChannelList() {
        try {
            getAppletContext().showDocument(
                    new java.net.URL(getTextParameter("HelpURL", DEFAULT_LIST_URL)),
                    "target window");
        } catch (java.net.MalformedURLException e) {
            sendToUser(
                    "[E] Could not load channel list page, bad URL in configuration: "
                    + e.getMessage());
        }
    }

    private void showHelp() {
        try {
            getAppletContext().showDocument(
                    new java.net.URL(getTextParameter("HelpURL", DEFAULT_HELP_URL)),
                    "target window");
        } catch (java.net.MalformedURLException e) {
            sendToUser(
                    "[E] Could not load help page, bad URL in configuration: " + e.getMessage());
        }
    }

    public boolean showJoinsAndParts() {
        return chat.isDisplayingJoinsAndParts();
    }

    private int getNumericParameter(String parameterName, int defaultValue) {
        if (getParameter(parameterName) == null)
            return defaultValue;

        try {
            return Integer.parseInt(getParameter(parameterName));
        } catch (NumberFormatException nfe) {
            System.err.println("Configuration error: Applet parameter " + parameterName + " must be numeric");
            return defaultValue;
        }
    }

    private String getTextParameter(String parameterName, String defaultValue) {
        if (getParameter(parameterName) == null)
            return defaultValue;

        return getParameter(parameterName);
    }

    private boolean isBooleanParameterSet(String parameterName) {
        return getParameter(parameterName) != null
                && (getParameter(parameterName).equalsIgnoreCase("yes")
                || getParameter(parameterName).equalsIgnoreCase("true")
                || getParameter(parameterName).equalsIgnoreCase("y"));
    }

    private boolean isAServer(String source) {
        return source.indexOf(".") != -1;
    }

    private String extractEverythingAfter(String s, String subString) {
        return s.substring(s.indexOf(subString) + subString.length()).trim();
    }


    private boolean isAllowedNick(String nick) {
        for (int i = 0; i < allowedNicks.length; i++) {
            if (allowedNicks[i].equals(nick))
                return true;
        }
        return false;
    }

    private String[] createAllowedNicks() {
        StringTokenizer tok = new StringTokenizer(getTextParameter("AllowedNicks", ""));
        String[] allowedNicks = new String[tok.countTokens()];
        for (int i = 0; i < allowedNicks.length; i++) {
            allowedNicks[i] = tok.nextToken();
        }
        return allowedNicks;
    }

    public void addIgnore(String ignoreMask) {
	if(!EntryDialog.isValidBanmask(ignoreMask)) {
	    sendToUser("[E] This is an invalid mask.  It should be in the format of nick!user@host, with * as a wildcard.");
	} else {
	    String ignoreRegexp = "(?i:";
	    ignoreRegexp = ignoreRegexp.concat(ignoreMask + ")");
	    ignoreRegexp = ignoreRegexp.replaceAll("\\.","\\\\.");
	    ignoreRegexp = ignoreRegexp.replaceAll("\\*",".*");
	    ignoreRegexp = ignoreRegexp.replaceAll("\\[","\\\\[");
	    ignoreRegexp = ignoreRegexp.replaceAll("\\]","\\\\]");
	    ignoreRegexp = ignoreRegexp.replaceAll("\\^","\\\\^");
	    Pair p = new Pair(ignoreMask,ignoreRegexp);
	    IgnoreList.addElement(p);
	    sendToUser("[I] Added ignore for: " + ignoreMask);
	}
    }

    public void remIgnore(int index) {
	Pair p = (Pair)IgnoreList.get(index);
	IgnoreList.remove(index);
	sendToUser("[I] Successfully removed ignore: " + p.first);
    }

    public boolean isIgnored(String usermask) {
	int size = IgnoreList.size();

	if(size == 0)
	    return false;

	for(int i = 0; i < size; ++i) {
	    Pair p = (Pair)IgnoreList.get(i);
	    if(usermask.matches(p.second)) {
		return true;
	    }
	}

	return false;
    }
    
    public void showIgnoreList() {
	if(IgnoreList.isEmpty()) {
	    sendToUser("[I]The ignore list is empty.");
	} else {
		sendToUser("Usage: /ignore [add|remove] [mask|Number] \n" +
					"Ex. To remove the 1st ignore on the ignore list: /ignore remove 0");
	    sendToUser("Ignore List:\n");
	    for(int i = 0, size=IgnoreList.size(); i < size; ++i) {
		Pair p = (Pair)IgnoreList.get(i);
		sendToUser("[" + i + "] " + p.first);
	    }
	}
    }
}
