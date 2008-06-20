

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * <p>I feel this class should eventually go away.
 *
 * @version $Id: EntryDialog.java,v 1.6 2004/07/27 02:29:29 halcy0n Exp $
 */

public class EntryDialog extends Dialog implements ActionListener {
    private TextField entryField;
    private String result;

    public static final String VALID_NICK_CHARS =
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}|[]\\^-_";

    public void actionPerformed(ActionEvent e) {
        result = entryField.getText();
        this.dispose();
    }


    private static boolean isValidChannel(String channel) {
        if (channel.length() == 0)
            return false;

        for (int i = 0; i < channel.length(); i++) {
            if (channel.charAt(i) == ' '
                    || channel.charAt(i) == ('\007')
                    || channel.charAt(i) == (','))
                return false;
        }

        return true;
    }

    private static boolean isValidNick(String nick) {
        if (nick.length() == 0)
            return false;

        if (nick.charAt(0) == '-' || Character.isDigit(nick.charAt(0)))
            return false;

        for (int i = 0; i < nick.length(); i++) {
            if (VALID_NICK_CHARS.indexOf(nick.charAt(i)) == -1) {
                return false;
            }
        }

        return true;
    }

    public static String promptForChannel() {
        String channel = "";
        String error = "";

        while (!isValidChannel(channel)) {
            EntryDialog nickDialog = new EntryDialog("Enter a Channel to Join", error);
            nickDialog.show();
            channel = nickDialog.result;
            error = "Not a Valid Channel Name";
        }

        if (channel.charAt(0) != '#'
                && channel.charAt(0) != '&'
                && channel.charAt(0) != '+')
            return "#" + channel;

        return channel;
    }

    public static String promptForNick(String errorMessage) {
        String nick = "";

        while (!isValidNick(nick)) {
            EntryDialog nickDialog = new EntryDialog("Enter a New Nick-Name", errorMessage);
            nickDialog.show();
            nick = nickDialog.result;
            errorMessage = "Not a Valid Nick Name";
        }

        return nick;
    }

    public static String promptForNick() {
        return promptForNick("");
    }

    public static boolean isValidBanmask(String ban) {
	if(ban.matches(".+\\!.+\\@.+"))
	    return true;
	return false;
    }
    
    
    public static String promptForBanmask(String ban) {
	ban = "*!*@" + ban;
	
	EntryDialog banDialog = new EntryDialog("Enter a Ban Mask", "", ban);
	banDialog.show();
	ban = banDialog.result;

	return ban;
    }

    private EntryDialog(String title, String statusText) {
        super(new Frame(), true);

        this.setTitle(title);
        this.setModal(true);

        entryField = new TextField("", 20);
        entryField.addActionListener(this);
        this.add("North", entryField);
        Panel p = new Panel();
        p.setLayout(new FlowLayout(FlowLayout.CENTER));
        Button yes = new Button("Ok");
        yes.addActionListener(this);
        p.add(yes);

        this.add("Center", p);

        if (!statusText.equals("")) {
            TextField statusField = new TextField(statusText, 30);
            statusField.setEditable(false);
            statusField.setBackground(this.getBackground());
            this.add("South", statusField);
            this.setSize(250, 140);
        } else 
			this.setSize(250, 120);
			
        this.setLocation(100, 200);
    }
    
    private EntryDialog(String title, String statusText, String initalText) {
        super(new Frame(), true);

        this.setTitle(title);
        this.setModal(true);

        entryField = new TextField(initalText, 20);
        
        entryField.addActionListener(this);
        this.add("North", entryField);
        Panel p = new Panel();
        p.setLayout(new FlowLayout(FlowLayout.CENTER));
        Button yes = new Button("Ok");
        yes.addActionListener(this);
        p.add(yes);

        this.add("Center", p);

        if (!statusText.equals("")) {
            TextField statusField = new TextField(statusText, 30);
            statusField.setEditable(false);
            statusField.setBackground(this.getBackground());
            this.add("South", statusField);
            this.setSize(250, 140);
            
        } else 
			this.setSize(250, 120);
			
        this.setLocation(100, 200);
    }
}
